package com.careernavigator.service;

import com.careernavigator.dto.response.RoadmapResponse;
import com.careernavigator.entity.*;
import com.careernavigator.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * RoadmapService
 * Generates personalized learning roadmaps
 * based on student's top career match
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class RoadmapService {

    private final RoadmapRepository roadmapRepository;
    private final RoadmapMilestoneRepository milestoneRepository;
    private final CareerRecommendationRepository careerRepo;
    private final ProgressTrackingRepository progressRepo;
    private final UserRepository userRepository;

    // ==========================================
    // GENERATE ROADMAP
    // ==========================================
    @Transactional
    public RoadmapResponse generateRoadmap(
            String userEmail) {

        log.info("Generating roadmap for: {}",
                userEmail);

        // Find user
        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        // Get top career recommendation
        List<CareerRecommendation> recommendations =
                careerRepo.findByUserIdOrderByRankAsc(
                        user.getId()
                );

        if (recommendations.isEmpty()) {
            return RoadmapResponse.builder()
                    .success(false)
                    .message(
                            "Please complete quiz and " +
                                    "get career recommendations first!"
                    )
                    .build();
        }

        // Get top career
        String topCareer =
                recommendations.get(0).getCareerName();

        // Delete old roadmap for same career
        roadmapRepository.findByUserIdAndCareerName(
                user.getId(), topCareer
        ).ifPresent(r ->
                roadmapRepository.delete(r)
        );

        // Build milestones for career
        List<RoadmapMilestone> milestones =
                buildMilestones(topCareer);

        // Set first milestone as ACTIVE
        if (!milestones.isEmpty()) {
            milestones.get(0).setStatus(
                    RoadmapMilestone.MilestoneStatus.ACTIVE
            );
        }

        // Create roadmap
        Roadmap roadmap = Roadmap.builder()
                .user(user)
                .careerName(topCareer)
                .totalDuration(
                        getDuration(topCareer)
                )
                .difficultyLevel(
                        getDifficulty(topCareer)
                )
                .status(Roadmap.RoadmapStatus.IN_PROGRESS)
                .completionPercentage(0.0)
                .build();

        Roadmap savedRoadmap =
                roadmapRepository.save(roadmap);

        // Link milestones to roadmap
        milestones.forEach(m ->
                m.setRoadmap(savedRoadmap)
        );

        savedRoadmap.setMilestones(milestones);
        roadmapRepository.save(savedRoadmap);

        log.info(
                "Roadmap generated for {} → {}",
                userEmail, topCareer
        );

        return buildRoadmapResponse(
                savedRoadmap, true,
                "Roadmap generated successfully!"
        );
    }

    // ==========================================
    // GET MY ROADMAP
    // ==========================================
    public RoadmapResponse getMyRoadmap(
            String userEmail) {

        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        List<Roadmap> roadmaps =
                roadmapRepository
                        .findByUserIdOrderByCreatedAtDesc(
                                user.getId()
                        );

        if (roadmaps.isEmpty()) {
            return RoadmapResponse.builder()
                    .success(false)
                    .message(
                            "No roadmap found! " +
                                    "Generate your roadmap first!"
                    )
                    .build();
        }

        return buildRoadmapResponse(
                roadmaps.get(0), true,
                "Roadmap retrieved!"
        );
    }

    // ==========================================
    // COMPLETE MILESTONE
    // ==========================================
    @Transactional
    public RoadmapResponse completeMilestone(
            Long milestoneId,
            String userEmail) {

        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        // Find milestone
        RoadmapMilestone milestone =
                milestoneRepository
                        .findById(milestoneId)
                        .orElseThrow(() ->
                                new RuntimeException(
                                        "Milestone not found"
                                )
                        );

        // Mark as completed
        milestone.setIsCompleted(true);
        milestone.setStatus(
                RoadmapMilestone.MilestoneStatus.COMPLETED
        );
        milestoneRepository.save(milestone);

        // Save progress tracking
        ProgressTracking progress =
                ProgressTracking.builder()
                        .user(user)
                        .roadmap(milestone.getRoadmap())
                        .milestone(milestone)
                        .notes("Completed milestone: "
                                + milestone.getTitle())
                        .build();
        progressRepo.save(progress);

        // Unlock next milestone
        Roadmap roadmap = milestone.getRoadmap();
        List<RoadmapMilestone> allMilestones =
                milestoneRepository
                        .findByRoadmapIdOrderByMonthNumberAsc(
                                roadmap.getId()
                        );

        for (int i = 0;
             i < allMilestones.size() - 1; i++) {
            if (allMilestones.get(i).getId()
                    .equals(milestoneId)) {
                RoadmapMilestone next =
                        allMilestones.get(i + 1);
                if (next.getStatus() ==
                        RoadmapMilestone
                                .MilestoneStatus.LOCKED) {
                    next.setStatus(
                            RoadmapMilestone
                                    .MilestoneStatus.ACTIVE
                    );
                    milestoneRepository.save(next);
                }
                break;
            }
        }

        // Update completion percentage
        long completed = milestoneRepository
                .countByRoadmapIdAndIsCompleted(
                        roadmap.getId(), true
                );
        double percentage =
                ((double) completed /
                        allMilestones.size()) * 100;

        roadmap.setCompletionPercentage(percentage);
        roadmap.setUpdatedAt(LocalDateTime.now());

        // Check if fully completed
        if (percentage >= 100) {
            roadmap.setStatus(
                    Roadmap.RoadmapStatus.COMPLETED
            );
        }

        roadmapRepository.save(roadmap);

        log.info(
                "Milestone {} completed for {}. " +
                        "Progress: {}%",
                milestoneId, userEmail, percentage
        );

        return buildRoadmapResponse(
                roadmap, true,
                "Milestone completed! 🎉 " +
                        "Progress: " +
                        Math.round(percentage) + "%"
        );
    }

    // ==========================================
    // BUILD MILESTONE DATA PER CAREER
    // ==========================================
    private List<RoadmapMilestone> buildMilestones(
            String career) {

        return switch (career) {
            case "Web Development" ->
                    webDevMilestones();
            case "AI / Machine Learning" ->
                    aiMlMilestones();
            case "Data Science" ->
                    dataScienceMilestones();
            case "Cybersecurity" ->
                    cybersecurityMilestones();
            case "Cloud Computing" ->
                    cloudMilestones();
            default ->
                    webDevMilestones();
        };
    }

    // ==========================================
    // WEB DEV MILESTONES
    // ==========================================
    private List<RoadmapMilestone> webDevMilestones() {
        List<RoadmapMilestone> list = new ArrayList<>();

        list.add(RoadmapMilestone.builder()
                .monthNumber(1)
                .title("HTML & CSS Basics")
                .description(
                        "Learn the building blocks of web. " +
                                "Structure with HTML, style with CSS."
                )
                .topics(
                        "HTML tags, CSS selectors, " +
                                "Flexbox, Grid, Responsive design"
                )
                .resources(
                        "freeCodeCamp.org, " +
                                "W3Schools.com, " +
                                "CSS-Tricks.com"
                )
                .projectIdea(
                        "Build a personal portfolio website"
                )
                .estimatedHours(60)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(2)
                .title("JavaScript Fundamentals")
                .description(
                        "Learn programming logic with JS. " +
                                "DOM manipulation and ES6+ features."
                )
                .topics(
                        "Variables, Functions, Arrays, " +
                                "Objects, DOM, Events, Fetch API"
                )
                .resources(
                        "javascript.info, " +
                                "Eloquent JavaScript (free book), " +
                                "YouTube - Traversy Media"
                )
                .projectIdea(
                        "Build a To-Do List app with JS"
                )
                .estimatedHours(80)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(3)
                .title("React.js Basics")
                .description(
                        "Learn the most popular frontend " +
                                "framework for building UIs."
                )
                .topics(
                        "Components, Props, State, " +
                                "Hooks, useEffect, React Router"
                )
                .resources(
                        "React official docs (react.dev), " +
                                "Scrimba React course (free), " +
                                "YouTube - Codevolution"
                )
                .projectIdea(
                        "Build a Weather App using React"
                )
                .estimatedHours(90)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(4)
                .title("Node.js & Express Backend")
                .description(
                        "Build backend APIs with Node.js " +
                                "and Express framework."
                )
                .topics(
                        "Node.js basics, Express routing, " +
                                "REST APIs, Middleware, JWT auth"
                )
                .resources(
                        "The Odin Project (free), " +
                                "Node.js official docs, " +
                                "YouTube - Traversy Media"
                )
                .projectIdea(
                        "Build a REST API for a blog app"
                )
                .estimatedHours(90)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(5)
                .title("Database — MySQL & MongoDB")
                .description(
                        "Learn to store and retrieve data " +
                                "using SQL and NoSQL databases."
                )
                .topics(
                        "SQL basics, MySQL, MongoDB, " +
                                "Mongoose, CRUD operations, Joins"
                )
                .resources(
                        "SQLZoo.net (free), " +
                                "MongoDB University (free), " +
                                "YouTube - Academind"
                )
                .projectIdea(
                        "Add database to your blog API"
                )
                .estimatedHours(70)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(6)
                .title("Projects & Job Applications")
                .description(
                        "Build 3 strong portfolio projects " +
                                "and start applying for internships!"
                )
                .topics(
                        "Git & GitHub, Deployment, " +
                                "Resume writing, LinkedIn setup, " +
                                "Interview preparation"
                )
                .resources(
                        "Internshala.com, " +
                                "LinkedIn Jobs, " +
                                "GitHub Pages (free hosting)"
                )
                .projectIdea(
                        "Build Full Stack E-commerce App"
                )
                .estimatedHours(100)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        return list;
    }

    // ==========================================
    // AI/ML MILESTONES
    // ==========================================
    private List<RoadmapMilestone> aiMlMilestones() {
        List<RoadmapMilestone> list = new ArrayList<>();

        list.add(RoadmapMilestone.builder()
                .monthNumber(1)
                .title("Python Programming")
                .description(
                        "Learn Python — the primary language " +
                                "of AI and Machine Learning."
                )
                .topics(
                        "Python syntax, Functions, OOP, " +
                                "File handling, Libraries"
                )
                .resources(
                        "Python.org docs, " +
                                "Automate Boring Stuff (free book), " +
                                "YouTube - Corey Schafer"
                )
                .projectIdea(
                        "Build a simple Python calculator"
                )
                .estimatedHours(70)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(2)
                .title("Math for ML")
                .description(
                        "Study mathematics needed to " +
                                "understand ML algorithms."
                )
                .topics(
                        "Linear algebra, Statistics, " +
                                "Probability, Calculus basics"
                )
                .resources(
                        "Khan Academy (free), " +
                                "3Blue1Brown YouTube, " +
                                "StatQuest YouTube"
                )
                .projectIdea(
                        "Implement basic statistics in Python"
                )
                .estimatedHours(60)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(3)
                .title("NumPy & Pandas")
                .description(
                        "Master data manipulation libraries " +
                                "used in every ML project."
                )
                .topics(
                        "NumPy arrays, Pandas DataFrames, " +
                                "Data cleaning, EDA"
                )
                .resources(
                        "Kaggle Learn (free), " +
                                "Pandas official docs, " +
                                "YouTube - Keith Galli"
                )
                .projectIdea(
                        "Analyze a real dataset from Kaggle"
                )
                .estimatedHours(70)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(4)
                .title("ML Algorithms")
                .description(
                        "Learn core machine learning " +
                                "algorithms with Scikit-learn."
                )
                .topics(
                        "Linear regression, Decision trees, " +
                                "KNN, SVM, Clustering, Model evaluation"
                )
                .resources(
                        "Scikit-learn docs, " +
                                "Google ML Crash Course (free), " +
                                "Kaggle Learn"
                )
                .projectIdea(
                        "Build a house price predictor"
                )
                .estimatedHours(90)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(5)
                .title("Deep Learning Basics")
                .description(
                        "Understand neural networks " +
                                "using TensorFlow and Keras."
                )
                .topics(
                        "Neural networks, Backpropagation, " +
                                "CNNs, Transfer learning"
                )
                .resources(
                        "fast.ai (free), " +
                                "TensorFlow tutorials, " +
                                "YouTube - Sentdex"
                )
                .projectIdea(
                        "Build an image classifier"
                )
                .estimatedHours(100)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(6)
                .title("Kaggle & Job Applications")
                .description(
                        "Compete on Kaggle and apply " +
                                "for AI/ML internships!"
                )
                .topics(
                        "Kaggle competitions, " +
                                "Feature engineering, " +
                                "Model deployment, Resume"
                )
                .resources(
                        "Kaggle.com (free), " +
                                "Internshala, LinkedIn Jobs"
                )
                .projectIdea(
                        "Complete a Kaggle competition"
                )
                .estimatedHours(100)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        return list;
    }

    // ==========================================
    // DATA SCIENCE MILESTONES
    // ==========================================
    private List<RoadmapMilestone> dataScienceMilestones() {
        List<RoadmapMilestone> list = new ArrayList<>();

        list.add(RoadmapMilestone.builder()
                .monthNumber(1)
                .title("Python & SQL Basics")
                .description("Learn Python and SQL — the two most essential tools for data professionals.")
                .topics("Python basics, SQL SELECT, Joins, Aggregations")
                .resources("Mode SQL Tutorial (free), Kaggle Python course")
                .projectIdea("Analyze a sales database with SQL")
                .estimatedHours(65)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(2)
                .title("Data Analysis with Pandas")
                .description("Deep dive into Pandas for data manipulation and analysis.")
                .topics("DataFrames, Data cleaning, GroupBy, Merging, EDA")
                .resources("Pandas docs, Kaggle Learn, YouTube - Keith Galli")
                .projectIdea("Clean and analyze messy Kaggle dataset")
                .estimatedHours(70)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(3)
                .title("Data Visualization")
                .description("Tell stories with data using charts and dashboards.")
                .topics("Matplotlib, Seaborn, Plotly, Dashboard design")
                .resources("Seaborn docs, Storytelling with Data (book)")
                .projectIdea("Create a data dashboard for COVID data")
                .estimatedHours(60)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(4)
                .title("Statistics & Probability")
                .description("Build the statistical foundation needed for data science.")
                .topics("Descriptive stats, Hypothesis testing, Correlation, A/B testing")
                .resources("StatQuest YouTube (free), Khan Academy")
                .projectIdea("Run A/B test analysis on real data")
                .estimatedHours(65)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(5)
                .title("Machine Learning Basics")
                .description("Apply ML algorithms to real datasets.")
                .topics("Scikit-learn, Regression, Classification, Model evaluation")
                .resources("Scikit-learn docs, Kaggle ML course")
                .projectIdea("Predict customer churn using ML")
                .estimatedHours(85)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        return list;
    }

    // ==========================================
    // CYBERSECURITY MILESTONES
    // ==========================================
    private List<RoadmapMilestone> cybersecurityMilestones() {
        List<RoadmapMilestone> list = new ArrayList<>();

        list.add(RoadmapMilestone.builder()
                .monthNumber(1)
                .title("Networking Fundamentals")
                .description("Understand how networks work — the foundation of cybersecurity.")
                .topics("OSI model, TCP/IP, DNS, HTTP, Firewalls, VPNs")
                .resources("Professor Messer (free), CompTIA Net+ study guide")
                .projectIdea("Set up a home network and document it")
                .estimatedHours(60)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(2)
                .title("Linux Operating System")
                .description("Master Linux command line — used in 90% of security tools.")
                .topics("Linux file system, Shell commands, User permissions, Bash scripting")
                .resources("OverTheWire Bandit (free), Linux Journey")
                .projectIdea("Complete OverTheWire Bandit levels 1-10")
                .estimatedHours(65)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(3)
                .title("Python for Security")
                .description("Use Python to write security scripts and tools.")
                .topics("Python basics, Socket programming, Writing scanners")
                .resources("Black Hat Python book, Python.org")
                .projectIdea("Write a simple port scanner in Python")
                .estimatedHours(65)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(4)
                .title("Ethical Hacking")
                .description("Learn penetration testing methodology and attack techniques.")
                .topics("Reconnaissance, Scanning, Exploitation, Metasploit, Web attacks")
                .resources("TryHackMe (free), HackTheBox")
                .projectIdea("Complete TryHackMe Pre-Security path")
                .estimatedHours(90)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(5)
                .title("Certifications & Jobs")
                .description("Prepare for certifications and apply for security internships.")
                .topics("CompTIA Security+, CEH basics, eJPT exam prep")
                .resources("CompTIA official site, Internshala")
                .projectIdea("Create a security portfolio on GitHub")
                .estimatedHours(80)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        return list;
    }

    // ==========================================
    // CLOUD MILESTONES
    // ==========================================
    private List<RoadmapMilestone> cloudMilestones() {
        List<RoadmapMilestone> list = new ArrayList<>();

        list.add(RoadmapMilestone.builder()
                .monthNumber(1)
                .title("Linux & Networking Basics")
                .description("Learn Linux and networking — foundation for cloud engineering.")
                .topics("Linux commands, Networking, TCP/IP, DNS")
                .resources("Linux Journey (free), Professor Messer")
                .projectIdea("Set up a Linux virtual machine")
                .estimatedHours(60)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(2)
                .title("AWS Cloud Basics")
                .description("Get started with Amazon Web Services — world's top cloud platform.")
                .topics("EC2, S3, IAM, VPC, Lambda, AWS CLI")
                .resources("AWS Free Tier, AWS Skill Builder (free)")
                .projectIdea("Deploy a simple website on AWS S3")
                .estimatedHours(70)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(3)
                .title("Docker & Containers")
                .description("Learn containerization with Docker.")
                .topics("Docker basics, Dockerfile, Docker Compose, Container networking")
                .resources("Docker official docs, YouTube - TechWorld with Nana")
                .projectIdea("Containerize a web application with Docker")
                .estimatedHours(70)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(4)
                .title("Kubernetes Basics")
                .description("Learn container orchestration with Kubernetes.")
                .topics("Pods, Deployments, Services, Ingress, Helm charts")
                .resources("KodeKloud (free tier), Kubernetes official docs")
                .projectIdea("Deploy app on Kubernetes cluster")
                .estimatedHours(80)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        list.add(RoadmapMilestone.builder()
                .monthNumber(5)
                .title("AWS Certification & Jobs")
                .description("Get AWS certified and apply for cloud internships!")
                .topics("AWS Cloud Practitioner exam, Resume, LinkedIn optimization")
                .resources("AWS Skill Builder, Internshala, LinkedIn Jobs")
                .projectIdea("Build and deploy a cloud-native app")
                .estimatedHours(90)
                .isCompleted(false)
                .status(RoadmapMilestone.MilestoneStatus.LOCKED)
                .build());

        return list;
    }

    // ==========================================
    // HELPER METHODS
    // ==========================================
    private String getDuration(String career) {
        return switch (career) {
            case "Web Development" -> "6 months";
            case "AI / Machine Learning" -> "12 months";
            case "Data Science" -> "8 months";
            case "Cybersecurity" -> "8 months";
            case "Cloud Computing" -> "8 months";
            default -> "6 months";
        };
    }

    private String getDifficulty(String career) {
        return switch (career) {
            case "Web Development" -> "Beginner Friendly";
            case "AI / Machine Learning" -> "Intermediate";
            case "Data Science" -> "Intermediate";
            case "Cybersecurity" -> "Intermediate";
            case "Cloud Computing" -> "Intermediate";
            default -> "Beginner Friendly";
        };
    }

    // Build response from Roadmap entity
    private RoadmapResponse buildRoadmapResponse(
            Roadmap roadmap,
            boolean success,
            String message) {

        List<RoadmapResponse.MilestoneDetail> details =
                roadmap.getMilestones() == null
                        ? new ArrayList<>()
                        : roadmap.getMilestones().stream()
                        .map(m ->
                                RoadmapResponse.MilestoneDetail
                                        .builder()
                                        .id(m.getId())
                                        .monthNumber(m.getMonthNumber())
                                        .title(m.getTitle())
                                        .description(m.getDescription())
                                        .topics(m.getTopics())
                                        .resources(m.getResources())
                                        .projectIdea(m.getProjectIdea())
                                        .estimatedHours(
                                                m.getEstimatedHours()
                                        )
                                        .isCompleted(m.getIsCompleted())
                                        .status(m.getStatus().name())
                                        .build()
                        )
                        .collect(Collectors.toList());

        long completed = details.stream()
                .filter(d -> Boolean.TRUE
                        .equals(d.getIsCompleted()))
                .count();

        return RoadmapResponse.builder()
                .success(success)
                .message(message)
                .roadmapId(roadmap.getId())
                .careerName(roadmap.getCareerName())
                .totalDuration(roadmap.getTotalDuration())
                .difficultyLevel(
                        roadmap.getDifficultyLevel()
                )
                .completionPercentage(
                        roadmap.getCompletionPercentage()
                )
                .status(roadmap.getStatus().name())
                .totalMilestones(details.size())
                .completedMilestones((int) completed)
                .milestones(details)
                .build();
    }
}