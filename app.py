from flask import Flask, render_template, request
import pdfplumber
import os
import re

app = Flask(__name__)
UPLOAD_FOLDER = "resume_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# FULL DATABASE (Ensure all roles are present)
BRANCH_DATA = {
        "Computer Science (CSE)": {
        "Full Stack Developer": ["react", "node.js", "mongodb", "javascript", "html", "css", "git", "rest api", "graphql", "next.js", "typescript", "express", "redux", "webpack", "docker"],
        "Backend Engineer": ["java", "spring boot", "sql", "docker", "python", "microservices", "redis", "postgresql", "fastapi", "golang", "flask", "django", "rabbitmq", "kafka", "orm"],
        "Cloud Architect": ["aws", "azure", "docker", "kubernetes", "terraform", "linux", "cloud computing", "s3", "ec2", "lambda", "iam", "vpc", "cloudformation", "eks", "ansible"],
        "Cybersecurity Analyst": ["wireshark", "metasploit", "penetration testing", "firewalls", "cryptography", "linux", "siem", "soc", "nmap", "vulnerability assessment", "burp suite", "owasp", "kali", "encryption", "ids/ips"],
        "Android Developer": ["kotlin", "java", "android studio", "xml", "mvvm", "retrofit", "firebase", "jetpack compose", "gradle", "coroutine", "dagger hilt", "rxjava", "sqlite", "material design", "activity lifecycle"],
        "Blockchain Engineer": ["solidity", "ethereum", "smart contracts", "web3", "rust", "cryptography", "hyperledger", "truffle", "ganache", "ipfs", "tokenomics", "defi", "consensus algorithms", "dapps", "polkadot"],
        "QA Automation": ["selenium", "junit", "test automation", "jira", "manual testing", "cucumber", "testng", "playwright", "postman", "cypress", "appium", "ci/cd", "regression testing", "loadrunner", "api testing"],
        "DevOps Engineer": ["jenkins", "ansible", "monitoring", "linux", "terraform", "bash", "prometheus", "grafana", "gitops", "cicd", "shell scripting", "helm", "argo cd", "nagios", "cloudwatch"],
        "UI/UX Designer": ["figma", "adobe xd", "wireframing", "prototyping", "user research", "sketch", "invision", "design system", "zeplin", "user journeys", "usability testing", "typography", "color theory", "interaction design", "accessibility"],
        "Software Architect": ["design patterns", "microservices", "system design", "scalability", "ddd", "clean architecture", "kafka", "soa", "monolith", "event-driven", "caching", "load balancing", "solid principles", "abstraction", "high availability"]
    },
    "AI & Machine Learning (AIML)": {
        "ML Engineer": ["python", "pytorch", "tensorflow", "scikit-learn", "numpy", "neural networks", "keras", "pandas", "huggingface", "transformers", "xgboost", "random forest", "gradient descent", "model deployment", "opencv"],
        "Data Scientist": ["pandas", "statistics", "sql", "tableau", "data visualization", "data mining", "r language", "power bi", "seaborn", "matplotlib", "probability", "jupyter", "hypothesis testing", "bigquery", "cleaning"],
        "NLP Engineer": ["transformers", "bert", "nltk", "spacy", "large language models", "prompt engineering", "gpt", "tokenization", "llm", "word2vec", "sentiment analysis", "langchain", "sequence labeling", "rag", "fasttext"],
        "Computer Vision Pro": ["opencv", "cnn", "yolo", "image processing", "pytorch", "deep learning", "segmentation", "resnet", "object detection", "gan", "mediapipe", "tensorflow lite", "image augmentation", "face recognition", "spatial AI"],
        "MLOps Engineer": ["mlflow", "kubeflow", "docker", "dvc", "bentoml", "fastapi", "cicd", "zenml", "monitoring", "model registry", "wandb", "feast", "data versioning", "pipelines", "serving"],
        "Data Engineer": ["spark", "hadoop", "etl", "data lake", "redshift", "airflow", "sql", "snowflake", "bigquery", "hive", "pyspark", "kafka", "dbt", "talend", "data modeling"],
        "Research Scientist": ["algorithms", "mathematics", "calculus", "linear algebra", "optimization", "publishing", "latex", "conference", "r&d", "peer review", "experiment design", "stochastic processes", "simulation", "bayesian", "theorems"],
        "Speech AI Specialist": ["asr", "tts", "signal processing", "audio analysis", "librosa", "transformers", "stt", "wav2vec", "speech-to-text", "acoustic modeling", "vocoders", "mfcc", "mel-spectrogram", "phonetics", "deepgram"],
        "Bioinformatics": ["genomics", "biopython", "molecular modeling", "ncbi", "r language", "matlab", "proteomics", "dna sequencing", "rna-seq", "phylogenetics", "alignment", "blast", "drug discovery", "protein folding", "cytoscape"],
        "AI Consultant": ["ai ethics", "strategy", "risk assessment", "llm", "fintech", "compliance", "policy", "business alignment", "roi", "governance", "explainable AI", "digital transformation", "stakeholder", "feasibility", "implementation"]
    },
    "Electronics (ECE)": {
        "VLSI Designer": ["verilog", "system verilog", "fpga", "cadence", "cmos", "digital electronics", "rtl", "asic", "vivado", "synopsys", "genus", "innovus", "sta", "physical design", "tcl"],
        "Embedded Developer": ["embedded c", "microcontrollers", "arm", "rtos", "i2c", "spi", "stm32", "can bus", "uart", "freeRTOS", "esp32", "bare metal", "debugging", "jtag", "logic analyzer"],
        "RF Engineer": ["antennas", "wireless", "dsp", "fourier transform", "modulation", "vna", "microwaves", "ads", "impedance", "smith chart", "lte", "5g", "spectrum analysis", "link budget", "hfss"],
        "Circuit Designer": ["pcb design", "altium", "analog circuits", "spice", "proteus", "kicad", "orcad", "layout", "multisim", "analog to digital", "op-amps", "signal integrity", "bom", "prototyping", "surface mount"],
        "IoT Architect": ["arduino", "raspberry pi", "mqtt", "node-red", "sensors", "lorawan", "zigbee", "esp32", "cloud connectivity", "coap", "edge computing", "ble", "iot gateway", "api", "dashboard"],
        "Signal Processing Eng": ["dsp", "matlab", "filter design", "wavelets", "fft", "signal modeling", "z-transform", "noise reduction", "adaptive filtering", "image compression", "sampling", "nyquist", "stft", "kalman filter", "spectral analysis"],
        "Firmware Engineer": ["linux kernel", "drivers", "assembly", "c++", "debugging", "jtag", "bare metal", "bootloader", "hal", "interrupts", "dma", "pci-e", "embedded linux", "yocto", "toolchain"],
        "Control Systems Eng": ["matlab", "simulink", "pid", "industrial automation", "plc programming", "feedback loops", "root locus", "stability", "state space", "lqr", "nyquist plot", "transfer function", "bode plot", "servos", "nonlinear control"],
        "Hardware QA": ["oscilloscope", "spectrum analyzer", "multimeter", "testing", "calibration", "logic analyzer", "emi", "bench testing", "validation", "thermal testing", "compliance", "iso 9001", "failure analysis", "documentation", "reliability"],
        "Telecom Manager": ["voip", "gsm", "lte", "5g", "spectrum management", "routing", "switching", "fiber optics", "sip", "sdn", "nfv", "oss/bss", "microwave links", "satellite", "network planning"]
    },
    "Electrical (EEE)": {
        "Power Systems Eng": ["power systems", "plc", "scada", "matlab", "relays", "switchgear", "etap", "load flow", "poweer quality", "smart grid", "high voltage", "transmission", "distribution", "fault analysis", "protection"],
        "EV Engineer": ["bms", "battery management", "electric motors", "powertrain", "can bus", "inverter", "thermal management", "charging infrastructure", "hevs", "regenerative braking", "li-ion", "motor control", "simulation", "dcdc converter", "automotive standards"],
        "Renewable Energy Pro": ["solar design", "wind turbines", "grid integration", "photovoltaics", "pvsyst", "energy storage", "hydroelectric", "biomass", "sustainability", "mppt", "inverters", "feasibility study", "clean tech", "epc", "homer"],
        "Automation Engineer": ["hmi", "dcs", "instrumentation", "sensors", "fieldbus", "plc", "ladder logic", "factorytalk", "tiaportal", "modbus", "profibus", "servo systems", "vfd", "commissioning", "control panels"],
        "Smart Grid Architect": ["microgrid", "distributed generation", "storage", "inverters", "demand response", "ami", "smart meter", "synchrophasor", "cybersecurity", "interoperability", "standards", "energy management", "peak shaving", "v2g", "renewables"],
        "Maintenance Eng": ["predictive maintenance", "tpm", "switchboard", "wiring", "diagnostics", "troubleshooting", "earthing", "preventive", "rcm", "root cause", "cmms", "safety protocols", "relays", "testing", "installation"],
        "Energy Auditor": ["energy efficiency", "iso 50001", "carbon", "lighting control", "hvac", "bems", "utility billing", "reporting", "ashrae", "benchmarking", "retrofitting", "cogeneration", "demand side", "payback analysis", "compliance"],
        "Protection Engineer": ["relays", "switchgear", "fault analysis", "etap", "coordination", "breaker", "current transformer", "voltage transformer", "differential protection", "distance protection", "arc flash", "selectivity", "settings", "commissioning", "standards"],
        "Lighting Designer": ["dialux", "relux", "photometrics", "led tech", "control systems", "luminaire", "ies", "glare evaluation", "daylighting", "specification", "renderings", "lux levels", "color rendering", "emergency lighting", "energy code"],
        "Instrumentation Eng": ["sensors", "transducers", "calibration", "analog digital", "labview", "data acquisition", "daq", "p&id", "loop tuning", "measurement", "signal conditioning", "fieldbus", "hart", "plc", "valves"]
    },
    "Mechanical (ME)": {
        "CAD Designer": ["solidworks", "catia", "nx cad", "autocad", "g-code", "3d modeling", "rendering", "drafting", "ptc creo", "geometric dimensioning", "tolerance analysis", "pdm", "surface modeling", "assembly", "prototyping"],
        "FEA Analyst": ["ansys", "hypermesh", "finite element analysis", "nastran", "simulation", "structural analysis", "boundary conditions", "meshing", "linear", "nonlinear", "fatigue", "vibration", "stress analysis", "thermal simulation", "abaqus"],
        "Thermal Engineer": ["thermodynamics", "heat transfer", "cfd", "hvac", "fluid mechanics", "refrigeration", "cooling systems", "conduction", "convection", "radiation", "heat exchangers", "simulation", "boiling", "condensation", "energy balance"],
        "Manufacturing Eng": ["cnc", "cam", "lean manufacturing", "six sigma", "kaizen", "qa", "jit", "kanban", "process optimization", "value stream", "quality control", "iso 9001", "tooling", "assembly line", "operations"],
        "Robotics Engineer": ["ros", "kinematics", "actuators", "control systems", "sensors", "path planning", "pathfinding", "inverse kinematics", "path planning", "vision systems", "end effectors", "simulation", "mechatronics", "uav", "automation"],
        "Automotive Engineer": ["engine design", "suspension", "aerodynamics", "hybrid systems", "chassis", "braking system", "powertrain", "vehicle dynamics", "hmi", "safety", "nvh", "materials", "crash testing", "diagnostics", "manufacturing"],
        "Maintenance Mgr": ["tpm", "reliability", "pumps", "compressors", "lubrication", "valves", "pdm", "cmms", "pumps", "bearings", "gears", "alignment", "condition monitoring", "safety", "scheduling"],
        "Aerospace Eng": ["propulsion", "avionics", "structural analysis", "turbines", "materials", "aerodynamics", "mach number", "lift", "drag", "flight mechanics", "composites", "wind tunnel", "orbital", "simulation", "standards"],
        "Plant Engineer": ["boilers", "utility systems", "safety management", "pumps", "inventory", "facilities", "osha", "pumps", "piping", "maintenance", "operations", "hvac", "power generation", "contractor management", "shutdown planning"],
        "HVAC Designer": ["psychrometry", "duct design", "chillers", "ventilation", "hvac", "cooling load", "vrf", "ahu", "vav", "controls", "refrigeration", "ashrae", "energy modeling", "piping", "commissioning"]
    },
    "AI & Data Science (AIDS)": {
        "Data Scientist": ["python", "sql", "predictive modeling", "statistics", "seaborn", "pandas", "linear regression", "clustering", "time series", "r", "tableau", "exploratory data", "hypothesis testing", "machine learning", "feature engineering"],
        "Data Lake Architect": ["spark", "hadoop", "snowflake", "databricks", "aws glue", "athena", "delta lake", "parquet", "storage", "cloud", "etl", "governance", "security", "pipelines", "scalability"],
        "BI Developer": ["power bi", "looker", "dashboards", "etl", "excel vba", "data modeling", "tableau", "dax", "sql", "reporting", "data warehouse", "kpis", "analysis", "data integration", "ssrs"],
        "Big Data Engineer": ["hive", "pyspark", "bigquery", "nosql", "impala", "pipelines", "kafka", "flink", "storm", "hbase", "cloud", "scrapping", "data ingestion", "optimization", "scalability"],
        "Cloud Data Analyst": ["s3", "redshift", "quicksight", "data warehouse", "kinesis", "cloud storage", "elt", "athena", "glue", "fargate", "cloudwatch", "optimization", "security", "reporting", "cost management"],
        "Information Security": ["data privacy", "gdpr", "compliance", "encryption", "anonymization", "soc2", "access control", "auditing", "risk assessment", "hipaa", "nist", "dlp", "threat modeling", "incident response", "policies"],
        "Quantitative Analyst": ["financial modeling", "r", "risk analysis", "monte carlo", "trading", "time series", "statistics", "matlab", "stochastic", "calculus", "pricing", "derivatives", "portfolio", "excel", "sql"],
        "Data Steward": ["governance", "metadata", "cataloging", "lineage", "quality rules", "mdm", "dama", "standards", "compliance", "security", "dictionary", "lifecycle", "policies", "master data", "curation"],
        "Market Analyst": ["google analytics", "crm", "segmentation", "churn prediction", "trends", "behavior", "excel", "sql", "tableau", "reporting", "forecasting", "surveys", "ab testing", "consumer insight", "kpis"],
        "AI Solutions Arch": ["llm", "integration", "api", "prompt engineering", "agentic workflows", "rag", "langchain", "vector db", "cloud", "scalability", "openai", "deployment", "mlops", "transformers", "strategy"]
    },
    "Civil Engineering": {
        "Structural Engineer": ["staad pro", "etabs", "revit", "concrete design", "steel structures", "load calculation", "eurocodes", "is codes", "foundation", "seismic", "dynamics", "bridge", "high rise", "optimization", "analysis"],
        "Site Engineer": ["construction management", "billing", "surveying", "estimation", "m-book", "execution", "quality control", "safety", "surveying", "concrete", "steel", "reports", "labor management", "planning", "site supervision"],
        "BIM Coordinator": ["revit", "navisworks", "bim 360", "3d modeling", "point cloud", "clash detection", "4d simulation", "vDC", "ifc", "standards", "collaboration", "architecture", "mep", "coordination", "interoperability"],
        "Geotechnical Engineer": ["soil mechanics", "foundation design", "plaxis", "seismology", "slope stability", "drilling", "retaining walls", "tunnels", "dams", "landslides", "exploration", "geo-environmental", "ground improvement", "rock mechanics", "laboratory testing"],
        "Quantity Surveyor": ["cost estimation", "tendering", "contracts", "autocad", "valuation", "boq", "rate analysis", "billing", "budgeting", "variation", "claims", "measurement", "procurement", "vba", "subcontracting"],
        "Transportation Engineer": ["traffic engineering", "gis", "pavement design", "vissim", "mx road", "highway design", "alignment", "infrastructure", "simulation", "public transport", "safety", "modeling", "its", "rail", "airport"],
        "Environmental Engineer": ["water treatment", "waste management", "eia", "hydrology", "air quality", "sewage", "sustainability", "remediation", "compliance", "hse", "scrubbers", "renewable", "audit", "carbon footprint", "policy"],
        "Hydraulics Engineer": ["hec-ras", "epanet", "irrigation", "dams", "fluid dynamics", "stormwater", "open channel", "flood mapping", "drainage", "river engineering", "sediment transport", "pumps", "hydropower", "coastal", "software"],
        "Urban Planner": ["gis", "public policy", "sustainable design", "cad", "zoning", "master plan", "transport planning", "housing", "regeneration", "community", "environment", "economic development", "legislation", "land use", "stakeholder"],
        "Civil Project Manager": ["primavera", "ms project", "budgeting", "wbs", "scheduling", "pmp", "cpm", "pert", "risk", "contracts", "site", "labor", "cost control", "reporting", "stakeholder"]
    },
    "Mechatronics": {
        "Robotics Engineer": ["ros", "path planning", "kinematics", "lidar", "opencv", "c++", "trajectory", "kalman filter", "simulink", "automation", "actuators", "sensors", "embedded", "slamm", "simulation"],
        "Automation Lead": ["plc programming", "tia portal", "hmi", "scada", "motion control", "servo motors", "industrial automation", "fieldbus", "sensors", "integration", "commissioning", "safety", "network", "vfd", "troubleshooting"],
        "Embedded Systems": ["stm32", "rtos", "can open", "motor control", "encoders", "uart", "microchip", "embedded c", "i2c", "spi", "bare metal", "firmware", "iot", "testing", "pcb"],
        "System Integrator": ["sensors", "actuators", "plc", "vision systems", "industrial iot", "modbus", "profibus", "ethercat", "control panel", "testing", "wiring", "design", "specification", "hmi", "automation"],
        "Control Engineer": ["matlab", "pid", "kalman filter", "feedback loops", "stability", "state space", "lqr", "simulink", "dynamics", "optimization", "servo", "signal", "system", "identification", "modelling"],
        "UAV Developer": ["drones", "pixhawk", "mavlink", "autopilot", "telemetry", "flight control", "ardupilot", "gimbal", "vision", "gps", "propulsion", "aerodynamics", "ground station", "simulation", "testing"],
        "Machine Vision Eng": ["opencv", "image segmentation", "halcon", "industrial cameras", "lighting", "object recognition", "blob detection", "inspection", "ocr", "sorting", "algorithm", "python", "optics", "ai", "industrial"],
        "PLC Programmer": ["ladder logic", "scl", "allen bradley", "beckhoff", "ethercat", "function block", "twincat", "codesys", "automation", "hmi", "troubleshooting", "safety", "panels", "programming", "maintenance"],
        "Test Engineer": ["labview", "data acquisition", "hili", "sil", "validation", "instrumentation", "simulation", "v&v", "software", "hardware", "daq", "reporting", "testing", "systems", "standards"],
        "Product Designer": ["fusion 360", "3d printing", "prototyping", "mechanism design", "electronics", "catia", "ergonomics", "materials", "manufacturing", "sketching", "styling", "solidworks", "user interface", "ux", "rd"]
    },
    "Petroleum Engineering": {
        "Reservoir Engineer": ["petrel", "eclipse", "well logging", "fluid flow", "enhanced oil recovery", "decline curve", "simulation", "material balance", "pressure transient", "nodal analysis", "economics", "modeling", "geology", "field development", "management"],
        "Drilling Engineer": ["directional drilling", "mud weight", "well control", "offshore", "casing", "drill bit", "bop", "tally", "torque and drag", "fluid mechanics", "safety", "cementing", "exploration", "rig", "planning"],
        "Production Engineer": ["artificial lift", "well optimization", "surface facility", "nodal analysis", "plunger lift", "choke management", "workover", "integrity", "chemicals", "flow assurance", "multiphase", "separation", "gas lift", "esp", "maintenance"],
        "Petrophysicist": ["well logs", "porosity", "saturation", "lithology", "core analysis", "resistivity", "sonic logs", "nmr", "petrophysics", "geology", "mapping", "software", "statistics", "data quality", "reservoir"],
        "Operations": ["safety", "scheduling", "procurement", "maintenance", "drilling", "field ops", "compliance", "logistics", "budget", "reporting", "supervision", "crew", "hse", "on-site", "emergency"],
        "Safety Officer": ["hazid", "hazop", "osha", "emergency response", "process safety", "ppe", "hse management", "audit", "risk", "environment", "permits", "toolbox", "compliance", "inspection", "reports"],
        "Completion Engineer": ["well testing", "hydraulic fracturing", "liner", "packers", "tubing", "fracture design", "acidizing", "stimulations", "wireline", "plugs", "coiled tubing", "fluids", "supervision", "perforating", "tools"],
        "Geoscientist": ["seismic", "mapping", "exploration", "gis", "earth modeling", "structural geology", "stratigraphy", "petroleum", "geochemistry", "basin analysis", "interpretation", "well tie", "gravity", "magnetic", "field study"],
        "Pipeline Engineer": ["corrosion", "pumping", "hydraulics", "gis", "inspection", "pigging", "asme b31.4", "cathodic protection", "valves", "stations", "routing", "construction", "integrity", "leak detection", "scada"],
        "Field Engineer": ["on-site", "logging", "maintenance", "troubleshooting", "safety", "crew management", "reporting", "well site", "supervision", "equipment", "logging", "testing", "calibration", "coordination", "ops"]
    },
    "Biotechnology": {
        "Bioinformatics": ["genomics", "sequencing", "biopython", "r language", "molecular modeling", "ncbi", "alignment", "blast", "proteomics", "phylo", "perl", "linux", "bioconductor", "crispr", "data mining"],
        "Lab Technician": ["pcr", "hplc", "cell culture", "gmp", "glp", "biosafety", "pipetting", "centrifuge", "titration", "spectroscopy", "buffer preparation", "gel electrophoresis", "incubation", "autoclave", "sop"],
        "R&D Scientist": ["assay development", "immunology", "protein purification", "cloning", "crispr", "elisa", "western blot", "drug discovery", "synthetic biology", "in-vitro", "spectrophotometry", "molecular biology", "rnaseq", "flow cytometry", "biochemistry"],
        "Clinical Analyst": ["ctms", "data management", "protocol", "regulations", "safety", "trial metrics", "ich-gcp", "clinical trials", "biostatistics", "sas", "data cleaning", "patient recruitment", "pharmacovigilance", "e-crf", "fda"],
        "Bioprocess Eng": ["fermentation", "bioreactor", "scale up", "downstream", "purification", "mass transfer", "upstream", "bioprocessing", "sterilization", "atps", "chromatography", "validation", "doe", "process control", "hplc"],
        "Quality Assurance": ["iso 13485", "gmp", "audit", "validation", "sop", "compliance", "corrective action", "documentation", "quality control", "risk management", "iso 9001", "regulatory affairs", "inspections", "capa", "qc lab"],
        "Molecular Biologist": ["dna", "rna", "electrophoresis", "sequencing", "genetics", "cloning", "transfection", "pcr", "crispr", "mutation analysis", "recombinant dna", "vector design", "genotyping", "microscopy", "rna-seq"],
        "Medical Writer": ["scientific writing", "submission", "data summary", "journal", "abstract", "manuscript", "ama style", "regulatory documents", "clinical study report", "investigator brochure", "medline", "pubmed", "peer review", "editing", "lit review"],
        "Regulatory Affairs": ["fda", "ema", "ce marking", "submission", "compliance", "strategy", "investigational new drug", "mhra", "safety reporting", "clinical trial application", "labeling", "regulatory CMC", "gmp audit", "orphan drug", "post-market"],
        "Genetics Counselor": ["ancestry", "disease marker", "data analysis", "ethics", "counseling", "inheritance", "pedigree", "prenatal", "cancer genetics", "variant interpretation", "syndromes", "chromosomal", "psychosocial", "patient advocacy", "genomics"]
    },
    "Aerospace": {
        "Propulsion": ["gas turbines", "combustion", "nozzles", "thermodynamics", "ansys", "fluid dynamics", "compressors", "rocket engines", "staged combustion", "cryogenics", "thermal analysis", "propellants", "specific impulse", "heat transfer", "nozzle flow"],
        "Avionics": ["flight controls", "radar", "navigation", "telemetry", "systems engineering", "avionics suite", "fms", "arinc 429", "mil-std-1553", "embedded systems", "sensors", "inertial navigation", "flight data", "uav electronics", "cockpit systems"],
        "Aerodynamics": ["cfd", "wind tunnel", "drag reduction", "airfoils", "mach number", "lift coefficient", "stability", "stokes flow", "vortex", "supersonic", "laminar", "turbulence modeling", "star-ccm+", "openfoam", "ansys fluent"],
        "Structural Analyst": ["nastran", "patran", "fatigue", "composites", "metallic structures", "crack growth", "structural test", "stress analysis", "vibration", "modal analysis", "buckling", "optimization", "materials testing", "fea", "cad"],
        "Flight Mechanics": ["stability", "orbital mechanics", "trajectory", "simulation", "control theory", "flight dynamics", "perturbation", "attitude control", "space mechanics", "gnc", "autopilot", "maneuvering", "re-entry", "keplerian", "state vector"],
        "Spacecraft Eng": ["satellite design", "thermal control", "payload", "solar arrays", "link budget", "orbital insertion", "ground segment", "vacuum testing", "rad-hard", "propulsion", "telemetry", "mechanical integration", "structure", "star tracker", "reaction wheel"],
        "Aero Design": ["catia", "nx", "conceptual design", "weights", "performance", "lofting", "specification", "igES", "3d modeling", "igads", "optimization", "aerostructures", "blueprints", "pdm", "surface modeling"],
        "Systems Integration": ["mil-std", "validation", "verification", "traceability", "interface", "system of systems", "requirements", "safety analysis", "fmea", "integration plan", "lifecycle", "testing", "systems engineering", "pmp", "quality"],
        "Payload Engineer": ["sensors", "cameras", "comms", "data handling", "integration", "optics", "spectrometer", "radiometry", "calibration", "data link", "payload testing", "thermal", "mass budget", "interface control", "power budget"],
        "Maintenance (AOG)": ["mro", "faa", "easa", "safety", "inspection", "quality", "parts procurement", "repair shop", "airworthiness", "engine overhaul", "maintenance planning", "logistics", "avionics repair", "safety management", "reporting"]
    },
    "Management (MBA)": {
        "Financial Analyst": ["modeling", "excel vba", "valuation", "sap", "audit", "corporate finance", "accounting", "p&l", "equity research", "risk assessment", "forecasting", "capital budgeting", "mergers", "cfa", "gaap"],
        "Marketing Manager": ["seo", "crm", "branding", "google analytics", "digital strategy", "market research", "advertising", "roi", "segmentation", "content strategy", "social media", "campaign management", "copywriting", "competitor analysis", "sales funnel"],
        "Supply Chain": ["logistics", "procurement", "erp", "forecasting", "lean", "warehouse", "inventory", "six sigma", "inventory management", "vendor relations", "distribution", "demand planning", "just-in-time", "sap scm", "sourcing"],
        "HR Manager": ["recruitment", "payroll", "compliance", "engagement", "hris", "talent", "employee relations", "labor law", "performance management", "onboarding", "succession planning", "conflict resolution", "compensation", "training", "culture"],
        "Operations": ["process improvement", "six sigma", "agile", "lean", "optimization", "erp", "productivity", "supply chain", "workflow", "capacity planning", "quality control", "kaizen", "cost reduction", "benchmarking", "operational excellence"],
        "Strategy Consultant": ["market entry", "swot", "transformation", "presentation", "risk", "business case", "frameworks", "strategic planning", "financial modeling", "stakeholder management", "change management", "market sizing", "feasibility", "management consulting", "data synthesis"],
        "Product Manager": ["roadmap", "backlog", "user stories", "ux", "agile", "wireframing", "mvp", "market fit", "scrum", "product lifecycle", "prioritization", "competitor research", "user testing", "kpis", "jira"],
        "Risk Manager": ["mitigation", "insurance", "quantitative", "compliance", "audit", "credit risk", "market risk", "basel", "hedging", "enterprise risk", "solvency", "stress testing", "risk appetite", "sox", "operational risk"],
        "Sales Director": ["b2b", "territory", "revenue", "crm", "negotiation", "prospecting", "forecast", "pipeline", "sales strategy", "key account", "lead generation", "quotas", "sales enablement", "client relations", "closing"],
        "Project Manager": ["jira", "pmp", "scrum", "budgeting", "resource", "ms project", "stakeholder", "timeline", "risk management", "wbs", "critical path", "pert", "gantt", "agile management", "kanban"]
    },
    "Petroleum Engineering": {
        "Reservoir Engineer": ["petrel", "eclipse", "well logging", "fluid flow", "enhanced oil recovery", "decline curve", "simulation", "material balance", "pressure transient", "nodal analysis", "economics", "modeling", "geology", "field development", "management"],
        "Drilling Engineer": ["directional drilling", "mud weight", "well control", "offshore", "casing", "drill bit", "bop", "tally", "torque and drag", "fluid mechanics", "safety", "cementing", "exploration", "rig", "planning"],
        "Production Engineer": ["artificial lift", "well optimization", "surface facility", "nodal analysis", "plunger lift", "choke management", "workover", "integrity", "chemicals", "flow assurance", "multiphase", "separation", "gas lift", "esp", "maintenance"],
        "Petrophysicist": ["well logs", "porosity", "saturation", "lithology", "core analysis", "resistivity", "sonic logs", "nmr", "petrophysics", "geology", "mapping", "software", "statistics", "data quality", "reservoir"],
        "Operations": ["safety", "scheduling", "procurement", "maintenance", "drilling", "field ops", "compliance", "logistics", "budget", "reporting", "supervision", "crew", "hse", "on-site", "emergency"],
        "Safety Officer": ["hazid", "hazop", "osha", "emergency response", "process safety", "ppe", "hse management", "audit", "risk", "environment", "permits", "toolbox", "compliance", "inspection", "reports"],
        "Completion Engineer": ["well testing", "hydraulic fracturing", "liner", "packers", "tubing", "fracture design", "acidizing", "stimulations", "wireline", "plugs", "coiled tubing", "fluids", "supervision", "perforating", "tools"],
        "Geoscientist": ["seismic", "mapping", "exploration", "gis", "earth modeling", "structural geology", "stratigraphy", "petroleum", "geochemistry", "basin analysis", "interpretation", "well tie", "gravity", "magnetic", "field study"],
        "Pipeline Engineer": ["corrosion", "pumping", "hydraulics", "gis", "inspection", "pigging", "asme b31.4", "cathodic protection", "valves", "stations", "routing", "construction", "integrity", "leak detection", "scada"],
        "Field Engineer": ["on-site", "logging", "maintenance", "troubleshooting", "safety", "crew management", "reporting", "well site", "supervision", "equipment", "calibration", "coordination", "ops"]
    },
    "Cybersecurity": {
        "Pentester": ["kali linux", "metasploit", "wireshark", "burp suite", "ethical hacking", "owasp", "red team", "nmap", "vulnerability scan", "shellcode", "sql injection", "xss", "exploitation", "scripting", "enumeration"],
        "Security Architect": ["firewalls", "zero trust", "iam", "iso 27001", "encryption", "siem", "proxies", "hsm", "security policy", "vpn", "pki", "casb", "infrastructure", "risk mitigation", "threat modeling"],
        "SOC Analyst": ["incident response", "log analysis", "splunk", "threat hunting", "detection", "soar", "edr", "incident management", "siem", "ids/ips", "packet capture", "forensics", "mfa", "alerts", "tcp/ip"],
        "Compliance Officer": ["nist", "hipaa", "soc2", "audit", "risk management", "policy", "grc", "gdpr", "sox", "pci-dss", "security controls", "governance", "remediation", "standards", "itgc"],
        "Cloud Security": ["aws guardduty", "azure sentinel", "casb", "serverless security", "iam", "cspm", "cwpp", "cloud security posture", "lambda security", "tenant", "s3 security", "cloudwatch", "containers", "eks", "fargate"],
        "Malware Analyst": ["reverse engineering", "sandbox", "static analysis", "dynamic analysis", "assembly", "ghidra", "ida pro", "ollydbg", "peid", "binary analysis", "obfuscation", "shellcode", "disassembler", "threat intel", "rootkits"],
        "Forensic Expert": ["encase", "ftk", "chain of custody", "recovery", "investigation", "memory dump", "autopsy", "digital evidence", "imaging", "forensic extraction", "cyber crime", "metadata", "volatility", "pcap", "write blocker"],
        "Network Security": ["vpn", "ips", "ids", "firewalls", "proxy", "wireshark", "ipsec", "radius", "routing", "dnssec", "subnetting", "vlans", "dmz", "bgp", "encryption"],
        "App Security": ["sast", "dast", "code review", "secure coding", "api security", "fuzzing", "dependency check", "burp suite", "owasp top 10", "fortify", "checkmarx", "security testing", "mitigation", "devsecops", "ci/cd"],
        "Threat Intel": ["osint", "dark web", "attribution", "iocs", "threat modeling", "stix", "taxii", "misp", "feed", "indicators", "adversary", "campaign", "tactics", "mitre att&ck", "analysis"]
    },
    "Biotechnology": {
        "Bioinformatics": ["genomics", "sequencing", "biopython", "r language", "molecular modeling", "ncbi", "alignment", "blast", "proteomics", "phylo", "perl", "linux", "bioconductor", "crispr", "data mining"],
        "Lab Technician": ["pcr", "hplc", "cell culture", "gmp", "glp", "biosafety", "pipetting", "centrifuge", "titration", "spectroscopy", "buffer preparation", "gel electrophoresis", "incubation", "autoclave", "sop"],
        "R&D Scientist": ["assay development", "immunology", "protein purification", "cloning", "crispr", "elisa", "western blot", "drug discovery", "synthetic biology", "in-vitro", "spectrophotometry", "molecular biology", "rnaseq", "flow cytometry", "biochemistry"],
        "Clinical Analyst": ["ctms", "data management", "protocol", "regulations", "safety", "trial metrics", "ich-gcp", "clinical trials", "biostatistics", "sas", "data cleaning", "patient recruitment", "pharmacovigilance", "e-crf", "fda"],
        "Bioprocess Eng": ["fermentation", "bioreactor", "scale up", "downstream", "purification", "mass transfer", "upstream", "bioprocessing", "sterilization", "atps", "chromatography", "validation", "doe", "process control", "hplc"],
        "Quality Assurance": ["iso 13485", "gmp", "audit", "validation", "sop", "compliance", "corrective action", "documentation", "quality control", "risk management", "iso 9001", "regulatory affairs", "inspections", "capa", "qc lab"],
        "Molecular Biologist": ["dna", "rna", "electrophoresis", "sequencing", "genetics", "cloning", "transfection", "pcr", "crispr", "mutation analysis", "recombinant dna", "vector design", "genotyping", "microscopy", "rna-seq"],
        "Medical Writer": ["scientific writing", "submission", "data summary", "journal", "abstract", "manuscript", "ama style", "regulatory documents", "clinical study report", "investigator brochure", "medline", "pubmed", "peer review", "editing", "lit review"],
        "Regulatory Affairs": ["fda", "ema", "ce marking", "submission", "compliance", "strategy", "investigational new drug", "mhra", "safety reporting", "clinical trial application", "labeling", "regulatory CMC", "gmp audit", "orphan drug", "post-market"],
        "Genetics Counselor": ["ancestry", "disease marker", "data analysis", "ethics", "counseling", "inheritance", "pedigree", "prenatal", "cancer genetics", "variant interpretation", "syndromes", "chromosomal", "psychosocial", "patient advocacy", "genomics"],
        "Bioinformatics": ["genomics", "sequencing", "biopython", "r language", "molecular modeling", "ncbi", "alignment", "blast", "proteomics", "phylo", "perl", "linux", "bioconductor", "crispr", "data mining"],
        "Lab Technician": ["pcr", "hplc", "cell culture", "gmp", "glp", "biosafety", "pipetting", "centrifuge", "titration", "spectroscopy", "buffer preparation", "gel electrophoresis", "incubation", "autoclave", "sop"],
        "R&D Scientist": ["assay development", "immunology", "protein purification", "cloning", "crispr", "elisa", "western blot", "drug discovery", "synthetic biology", "in-vitro", "spectrophotometry", "molecular biology", "rnaseq", "flow cytometry", "biochemistry"],
        "Clinical Analyst": ["ctms", "data management", "protocol", "regulations", "safety", "trial metrics", "ich-gcp", "clinical trials", "biostatistics", "sas", "data cleaning", "patient recruitment", "pharmacovigilance", "e-crf", "fda"],
        "Bioprocess Eng": ["fermentation", "bioreactor", "scale up", "downstream", "purification", "mass transfer", "upstream", "bioprocessing", "sterilization", "atps", "chromatography", "validation", "doe", "process control", "hplc"],
        "Quality Assurance": ["iso 13485", "gmp", "audit", "validation", "sop", "compliance", "corrective action", "documentation", "quality control", "risk management", "iso 9001", "regulatory affairs", "inspections", "capa", "qc lab"],
        "Molecular Biologist": ["dna", "rna", "electrophoresis", "sequencing", "genetics", "cloning", "transfection", "pcr", "crispr", "mutation analysis", "recombinant dna", "vector design", "genotyping", "microscopy", "rna-seq"],
        "Medical Writer": ["scientific writing", "submission", "data summary", "journal", "abstract", "manuscript", "ama style", "regulatory documents", "clinical study report", "investigator brochure", "medline", "pubmed", "peer review", "editing", "lit review"],
        "Regulatory Affairs": ["fda", "ema", "ce marking", "submission", "compliance", "strategy", "investigational new drug", "mhra", "safety reporting", "clinical trial application", "labeling", "regulatory CMC", "gmp audit", "orphan drug", "post-market"],
        "Genetics Counselor": ["ancestry", "disease marker", "data analysis", "ethics", "counseling", "inheritance", "pedigree", "prenatal", "cancer genetics", "variant interpretation", "syndromes", "chromosomal", "psychosocial", "patient advocacy", "genomics"]
    },
    "Aerospace": {
        "Propulsion": ["gas turbines", "combustion", "nozzles", "thermodynamics", "ansys", "fluid dynamics", "compressors", "rocket engines", "staged combustion", "cryogenics", "thermal analysis", "propellants", "specific impulse", "heat transfer", "nozzle flow"],
        "Avionics": ["flight controls", "radar", "navigation", "telemetry", "systems engineering", "avionics suite", "fms", "arinc 429", "mil-std-1553", "embedded systems", "sensors", "inertial navigation", "flight data", "uav electronics", "cockpit systems"],
        "Aerodynamics": ["cfd", "wind tunnel", "drag reduction", "airfoils", "mach number", "lift coefficient", "stability", "stokes flow", "vortex", "supersonic", "laminar", "turbulence modeling", "star-ccm+", "openfoam", "ansys fluent"],
        "Structural Analyst": ["nastran", "patran", "fatigue", "composites", "metallic structures", "crack growth", "structural test", "stress analysis", "vibration", "modal analysis", "buckling", "optimization", "materials testing", "fea", "cad"],
        "Flight Mechanics": ["stability", "orbital mechanics", "trajectory", "simulation", "control theory", "flight dynamics", "perturbation", "attitude control", "space mechanics", "gnc", "autopilot", "maneuvering", "re-entry", "keplerian", "state vector"],
        "Spacecraft Eng": ["satellite design", "thermal control", "payload", "solar arrays", "link budget", "orbital insertion", "ground segment", "vacuum testing", "rad-hard", "propulsion", "telemetry", "mechanical integration", "structure", "star tracker", "reaction wheel"],
        "Aero Design": ["catia", "nx", "conceptual design", "weights", "performance", "lofting", "specification", "igES", "3d modeling", "igads", "optimization", "aerostructures", "blueprints", "pdm", "surface modeling"],
        "Systems Integration": ["mil-std", "validation", "verification", "traceability", "interface", "system of systems", "requirements", "safety analysis", "fmea", "integration plan", "lifecycle", "testing", "systems engineering", "pmp", "quality"],
        "Payload Engineer": ["sensors", "cameras", "comms", "data handling", "integration", "optics", "spectrometer", "radiometry", "calibration", "data link", "payload testing", "thermal", "mass budget", "interface control", "power budget"],
        "Maintenance (AOG)": ["mro", "faa", "easa", "safety", "inspection", "quality", "parts procurement", "repair shop", "airworthiness", "engine overhaul", "maintenance planning", "logistics", "avionics repair", "safety management", "reporting"]
    },
    "Management (MBA)": {
        "Financial Analyst": ["modeling", "excel vba", "valuation", "sap", "audit", "corporate finance", "accounting", "p&l", "equity research", "risk assessment", "forecasting", "capital budgeting", "mergers", "cfa", "gaap"],
        "Marketing Manager": ["seo", "crm", "branding", "google analytics", "digital strategy", "market research", "advertising", "roi", "segmentation", "content strategy", "social media", "campaign management", "copywriting", "competitor analysis", "sales funnel"],
        "Supply Chain": ["logistics", "procurement", "erp", "forecasting", "lean", "warehouse", "inventory", "six sigma", "inventory management", "vendor relations", "distribution", "demand planning", "just-in-time", "sap scm", "sourcing"],
        "HR Manager": ["recruitment", "payroll", "compliance", "engagement", "hris", "talent", "employee relations", "labor law", "performance management", "onboarding", "succession planning", "conflict resolution", "compensation", "training", "culture"],
        "Operations": ["process improvement", "six sigma", "agile", "lean", "optimization", "erp", "productivity", "supply chain", "workflow", "capacity planning", "quality control", "kaizen", "cost reduction", "benchmarking", "operational excellence"],
        "Strategy Consultant": ["market entry", "swot", "transformation", "presentation", "risk", "business case", "frameworks", "strategic planning", "financial modeling", "stakeholder management", "change management", "market sizing", "feasibility", "management consulting", "data synthesis"],
        "Product Manager": ["roadmap", "backlog", "user stories", "ux", "agile", "wireframing", "mvp", "market fit", "scrum", "product lifecycle", "prioritization", "competitor research", "user testing", "kpis", "jira"],
        "Risk Manager": ["mitigation", "insurance", "quantitative", "compliance", "audit", "credit risk", "market risk", "basel", "hedging", "enterprise risk", "solvency", "stress testing", "risk appetite", "sox", "operational risk"],
        "Sales Director": ["b2b", "territory", "revenue", "crm", "negotiation", "prospecting", "forecast", "pipeline", "sales strategy", "key account", "lead generation", "quotas", "sales enablement", "client relations", "closing"],
        "Project Manager": ["jira", "pmp", "scrum", "budgeting", "resource", "ms project", "stakeholder", "timeline", "risk management", "wbs", "critical path", "pert", "gantt", "agile management", "kanban"]
    },
    "Petroleum Engineering": {
        "Reservoir Engineer": ["petrel", "eclipse", "well logging", "fluid flow", "enhanced oil recovery", "decline curve", "simulation", "material balance", "pressure transient", "nodal analysis", "economics", "modeling", "geology", "field development", "management"],
        "Drilling Engineer": ["directional drilling", "mud weight", "well control", "offshore", "casing", "drill bit", "bop", "tally", "torque and drag", "fluid mechanics", "safety", "cementing", "exploration", "rig", "planning"],
        "Production Engineer": ["artificial lift", "well optimization", "surface facility", "nodal analysis", "plunger lift", "choke management", "workover", "integrity", "chemicals", "flow assurance", "multiphase", "separation", "gas lift", "esp", "maintenance"],
        "Petrophysicist": ["well logs", "porosity", "saturation", "lithology", "core analysis", "resistivity", "sonic logs", "nmr", "petrophysics", "geology", "mapping", "software", "statistics", "data quality", "reservoir"],
        "Operations": ["safety", "scheduling", "procurement", "maintenance", "drilling", "field ops", "compliance", "logistics", "budget", "reporting", "supervision", "crew", "hse", "on-site", "emergency"],
        "Safety Officer": ["hazid", "hazop", "osha", "emergency response", "process safety", "ppe", "hse management", "audit", "risk", "environment", "permits", "toolbox", "compliance", "inspection", "reports"],
        "Completion Engineer": ["well testing", "hydraulic fracturing", "liner", "packers", "tubing", "fracture design", "acidizing", "stimulations", "wireline", "plugs", "coiled tubing", "fluids", "supervision", "perforating", "tools"],
        "Geoscientist": ["seismic", "mapping", "exploration", "gis", "earth modeling", "structural geology", "stratigraphy", "petroleum", "geochemistry", "basin analysis", "interpretation", "well tie", "gravity", "magnetic", "field study"],
        "Pipeline Engineer": ["corrosion", "pumping", "hydraulics", "gis", "inspection", "pigging", "asme b31.4", "cathodic protection", "valves", "stations", "routing", "construction", "integrity", "leak detection", "scada"],
        "Field Engineer": ["on-site", "logging", "maintenance", "troubleshooting", "safety", "crew management", "reporting", "well site", "supervision", "equipment", "calibration", "coordination", "ops"]
    },
    "Cybersecurity": {
        "Pentester": ["kali linux", "metasploit", "wireshark", "burp suite", "ethical hacking", "owasp", "red team", "nmap", "vulnerability scan", "shellcode", "sql injection", "xss", "exploitation", "scripting", "enumeration"],
        "Security Architect": ["firewalls", "zero trust", "iam", "iso 27001", "encryption", "siem", "proxies", "hsm", "security policy", "vpn", "pki", "casb", "infrastructure", "risk mitigation", "threat modeling"],
        "SOC Analyst": ["incident response", "log analysis", "splunk", "threat hunting", "detection", "soar", "edr", "incident management", "siem", "ids/ips", "packet capture", "forensics", "mfa", "alerts", "tcp/ip"],
        "Compliance Officer": ["nist", "hipaa", "soc2", "audit", "risk management", "policy", "grc", "gdpr", "sox", "pci-dss", "security controls", "governance", "remediation", "standards", "itgc"],
        "Cloud Security": ["aws guardduty", "azure sentinel", "casb", "serverless security", "iam", "cspm", "cwpp", "cloud security posture", "lambda security", "tenant", "s3 security", "cloudwatch", "containers", "eks", "fargate"],
        "Malware Analyst": ["reverse engineering", "sandbox", "static analysis", "dynamic analysis", "assembly", "ghidra", "ida pro", "ollydbg", "peid", "binary analysis", "obfuscation", "shellcode", "disassembler", "threat intel", "rootkits"],
        "Forensic Expert": ["encase", "ftk", "chain of custody", "recovery", "investigation", "memory dump", "autopsy", "digital evidence", "imaging", "forensic extraction", "cyber crime", "metadata", "volatility", "pcap", "write blocker"],
        "Network Security": ["vpn", "ips", "ids", "firewalls", "proxy", "wireshark", "ipsec", "radius", "routing", "dnssec", "subnetting", "vlans", "dmz", "bgp", "encryption"],
        "App Security": ["sast", "dast", "code review", "secure coding", "api security", "fuzzing", "dependency check", "burp suite", "owasp top 10", "fortify", "checkmarx", "security testing", "mitigation", "devsecops", "ci/cd"],
        "Threat Intel": ["osint", "dark web", "attribution", "iocs", "threat modeling", "stix", "taxii", "misp", "feed", "indicators", "adversary", "campaign", "tactics", "mitre att&ck", "analysis"]
    }
}
def get_seo_analysis(text):
    """UNIQUE ENGINE: Detects branding themes and flags high-risk clichés."""
    cliche_dict = {
        "Fillers": ["hardworking", "passionate", "team player", "motivated", "self-starter"],
        "Vague": ["results-oriented", "dynamic", "professional", "experienced"],
        "Passive": ["responsible for", "assisted with", "helped in"]
    }
    text_low = text.lower()
    found_cliches = [word for cat in cliche_dict.values() for word in cat if word in text_low]
    
    # Identify Identity Themes (words > 6 letters)
    words = re.findall(r'\b[A-Za-z]{7,}\b', text)
    freq = {}
    for w in words: freq[w] = freq.get(w, 0) + 1
    top_themes = [t.capitalize() for t in sorted(freq, key=freq.get, reverse=True)[:6]]
    
    return {"themes": top_themes, "cliches": found_cliches}

def analyze_resume(text, branch, job_role):
    text_low = text.lower()
    branch_roles = BRANCH_DATA.get(branch, {})
    expected_skills = branch_roles.get(job_role, ["technical skills"])
    
    detected = [s for s in expected_skills if re.search(r'\b' + re.escape(s.lower()) + r'\b', text_low)]
    missing = [s for s in expected_skills if s not in detected]
            
    checklist = [
        {"label": "Contact Details (Email/Phone)", "status": bool(re.search(r'[\w\.-]+@[\w\.-]+', text_low))},
        {"label": "Portfolio (GitHub/LinkedIn)", "status": bool(re.search(r'github\.com|linkedin\.com', text_low))},
        {"label": "Professional Summary", "status": bool(re.search(r'summary|profile|objective', text_low))},
        {"label": "Skills Section Header", "status": bool(re.search(r'skills|competencies', text_low))},
        {"label": "Work/Internship Experience", "status": bool(re.search(r'experience|internship', text_low))},
        {"label": "Detailed Projects", "status": bool(re.search(r'projects|academic work', text_low))},
        {"label": "Education info", "status": bool(re.search(r'education|university|college|b\.tech', text_low))},
        {"label": "Certifications/Awards", "status": bool(re.search(r'achievement|certification|award', text_low))},
        {"label": "Quantitative Metrics (% or #)", "status": bool(re.search(r'\d+%', text_low))},
        {"label": "ATS Action Verbs", "status": bool(re.search(r'developed|optimized|engineered|managed', text_low))},
        {"label": "Standard Headings", "status": bool(re.search(r'education|skills|experience', text_low))},
        {"label": "Content Richness (>200 words)", "status": len(text.split()) > 200},
        {"label": "Specific Role Alignment", "status": len(detected) > 0}
    ]

    kw_score = (len(detected) / len(expected_skills) * 60) if expected_skills else 0
    cl_score = (sum(1 for i in checklist if i['status']) / 13 * 40)
    final_score = int(kw_score + cl_score)
    seo = get_seo_analysis(text)

    return {
        "score": final_score,
        "rating": "Excellent" if final_score >= 85 else "Good" if final_score >= 65 else "Average",
        "detected": detected,
        "missing": missing,
        "checklist": checklist,
        "seo_themes": seo["themes"],
        "seo_cliches": seo["cliches"],
        "density": round((len(detected) / (max(len(text.split()), 1)/100)), 2)
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        branch = request.form.get("branch")
        role = request.form.get("job_role")
        f = request.files.get("resume")
        if f and f.filename.endswith(".pdf"):
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            with pdfplumber.open(path) as pdf:
                text = " ".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            result = analyze_resume(text, branch, role)
    return render_template("index.html", branch_data=BRANCH_DATA, result=result, page="home")

@app.route("/about")
def about():
    return render_template("index.html", page="about")

@app.route("/process")
def process():
    return render_template("index.html", page="process")

if __name__ == "__main__":
    app.run(debug=True)
