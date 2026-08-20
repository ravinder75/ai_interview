import logging
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class JobProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def fetch_jobs(self, query: str = "Software", location: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch raw jobs from provider API/feed"""
        pass

    @abstractmethod
    def normalize_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize raw provider payload to unified schema"""
        pass

class GreenhouseProvider(JobProvider):
    """Greenhouse Public Job Board API Adapter (e.g. GitLab, Figma, Vercel, Zapier, DoorDash)"""
    def __init__(self, boards: Optional[List[str]] = None):
        self.boards = boards or ["gitlab", "figma", "vercel", "zapier", "doordash", "cloudflare"]

    @property
    def provider_name(self) -> str:
        return "Greenhouse"

    async def fetch_jobs(self, query: str = "Software", location: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        raw_list = []
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for board in self.boards:
                try:
                    res = await client.get(f"https://api.greenhouse.io/v1/boards/{board}/jobs", headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        data = res.json()
                        company_name = board.capitalize()
                        for item in data.get("jobs", []):
                            item["_company_name"] = company_name
                            item["_board"] = board
                            raw_list.append(item)
                except Exception as e:
                    logger.warning(f"Greenhouse board {board} fetch failed: {e}")
        return raw_list

    def normalize_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        apply_url = raw.get("absolute_url")
        title = raw.get("title")
        if not apply_url or not title:
            return None

        # Parse posting date
        updated_str = raw.get("updated_at") or raw.get("first_published")
        posted_at = datetime.now(timezone.utc)
        if updated_str:
            try:
                posted_at = date_parser.parse(updated_str)
            except Exception:
                pass

        location_name = raw.get("location", {}).get("name", "Remote") if isinstance(raw.get("location"), dict) else str(raw.get("location") or "Remote")
        is_remote = "remote" in location_name.lower() or "anywhere" in location_name.lower()
        is_hybrid = "hybrid" in location_name.lower()

        return {
            "external_id": str(raw.get("id")),
            "source": self.provider_name,
            "title": title.strip(),
            "company": raw.get("_company_name", "Greenhouse Partner"),
            "location": location_name,
            "city": location_name.split(",")[0].strip() if "," in location_name else location_name,
            "country": location_name.split(",")[-1].strip() if "," in location_name else "Global",
            "remote": is_remote,
            "hybrid": is_hybrid,
            "employment_type": "Full-time",
            "job_category": "Software Engineering",
            "experience_level": "Mid-Level",
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "USD",
            "salary_range": "Salary Not Disclosed",
            "description": f"Position: {title} at {raw.get('_company_name')}. Location: {location_name}.",
            "skills": ["Software Engineering", "API", "System Architecture", "Git"],
            "posted_at": posted_at,
            "apply_url": apply_url,
            "source_url": apply_url,
            "is_active": True,
            "raw_data": raw
        }

class LeverProvider(JobProvider):
    """Lever Public Postings API Adapter (e.g. Spotify, Palantir, Netflix, Roblox)"""
    def __init__(self, sites: Optional[List[str]] = None):
        self.sites = sites or ["spotify", "palantir", "roblox", "atlassian"]

    @property
    def provider_name(self) -> str:
        return "Lever"

    async def fetch_jobs(self, query: str = "Software", location: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        raw_list = []
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for site in self.sites:
                try:
                    res = await client.get(f"https://api.lever.co/v0/postings/{site}", headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        data = res.json()
                        for item in data:
                            item["_site"] = site
                            raw_list.append(item)
                except Exception as e:
                    logger.warning(f"Lever site {site} fetch failed: {e}")
        return raw_list

    def normalize_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        apply_url = raw.get("applyUrl") or raw.get("hostedUrl")
        title = raw.get("text")
        if not apply_url or not title:
            return None

        created_ms = raw.get("createdAt")
        posted_at = datetime.now(timezone.utc)
        if created_ms:
            try:
                posted_at = datetime.fromtimestamp(created_ms / 1000.0, tz=timezone.utc)
            except Exception:
                pass

        categories = raw.get("categories", {})
        loc = categories.get("location", "Remote")
        commitment = categories.get("commitment", "Full-time")
        workplace = raw.get("workplaceType", "remote")

        is_remote = workplace == "remote" or "remote" in loc.lower()
        is_hybrid = workplace == "hybrid" or "hybrid" in loc.lower()

        return {
            "external_id": str(raw.get("id")),
            "source": self.provider_name,
            "title": title.strip(),
            "company": raw.get("_site", "Lever Partner").capitalize(),
            "location": loc,
            "city": loc.split(",")[0].strip() if "," in loc else loc,
            "country": raw.get("country") or "Global",
            "remote": is_remote,
            "hybrid": is_hybrid,
            "employment_type": commitment,
            "job_category": categories.get("team", "Software Engineering"),
            "experience_level": "Mid-Level",
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "USD",
            "salary_range": "Salary Not Disclosed",
            "description": raw.get("descriptionPlain") or raw.get("description") or f"{title} position at {raw.get('_site')}",
            "skills": ["Python", "JavaScript", "TypeScript", "REST APIs", "SQL", "Git"],
            "posted_at": posted_at,
            "apply_url": apply_url,
            "source_url": raw.get("hostedUrl") or apply_url,
            "is_active": True,
            "raw_data": raw
        }

class AshbyProvider(JobProvider):
    """Ashby Public Job Board API Adapter (e.g. Linear, Ramp, OpenAI, Retool)"""
    def __init__(self, boards: Optional[List[str]] = None):
        self.boards = boards or ["Linear", "ramp", "retool"]

    @property
    def provider_name(self) -> str:
        return "Ashby"

    async def fetch_jobs(self, query: str = "Software", location: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        raw_list = []
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for board in self.boards:
                try:
                    res = await client.get(f"https://api.ashbyhq.com/posting-api/job-board/{board}", headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        data = res.json()
                        for item in data.get("jobs", []):
                            item["_board"] = board
                            raw_list.append(item)
                except Exception as e:
                    logger.warning(f"Ashby board {board} fetch failed: {e}")
        return raw_list

    def normalize_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        apply_url = raw.get("applyUrl") or raw.get("jobUrl")
        title = raw.get("title")
        if not apply_url or not title:
            return None

        published_str = raw.get("publishedAt")
        posted_at = datetime.now(timezone.utc)
        if published_str:
            try:
                posted_at = date_parser.parse(published_str)
            except Exception:
                pass

        loc = raw.get("locationName", "Remote")
        is_remote = raw.get("isRemote", False) or "remote" in loc.lower()

        return {
            "external_id": str(raw.get("id")),
            "source": self.provider_name,
            "title": title.strip(),
            "company": raw.get("_board", "Ashby Partner").capitalize(),
            "location": loc,
            "city": loc.split(",")[0].strip() if "," in loc else loc,
            "country": "Global",
            "remote": is_remote,
            "hybrid": False,
            "employment_type": raw.get("employmentType", "Full-time"),
            "job_category": raw.get("departmentName", "Software Engineering"),
            "experience_level": "Mid-Level",
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "USD",
            "salary_range": "Salary Not Disclosed",
            "description": raw.get("descriptionPlain") or f"{title} at {raw.get('_board')}",
            "skills": ["TypeScript", "React", "Node.js", "PostgreSQL", "GraphQL", "Git"],
            "posted_at": posted_at,
            "apply_url": apply_url,
            "source_url": apply_url,
            "is_active": True,
            "raw_data": raw
        }

class AdzunaProvider(JobProvider):
    """Adzuna Job Search API Adapter (Supports Global & India - country code 'in')"""
    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        self.app_id = app_id
        self.app_key = app_key

    @property
    def provider_name(self) -> str:
        return "Adzuna"

    async def fetch_jobs(self, query: str = "Software", location: str = "in", max_results: int = 25) -> List[Dict[str, Any]]:
        raw_list = []
        if not self.app_id or not self.app_key:
            return raw_list

        country_code = "in" if "ind" in location.lower() or location.lower() in ["in", "india"] else "gb"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(
                    f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1",
                    params={
                        "app_id": self.app_id,
                        "app_key": self.app_key,
                        "results_per_page": max_results,
                        "what": query
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    raw_list = data.get("results", [])
            except Exception as e:
                logger.warning(f"Adzuna API fetch failed for {country_code}: {e}")
        return raw_list

    def normalize_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        apply_url = raw.get("redirect_url")
        title = raw.get("title")
        if not apply_url or not title:
            return None

        created_str = raw.get("created")
        posted_at = datetime.now(timezone.utc)
        if created_str:
            try:
                posted_at = date_parser.parse(created_str)
            except Exception:
                pass

        loc_data = raw.get("location", {})
        display_name = loc_data.get("display_name", "UK") if isinstance(loc_data, dict) else "UK"

        return {
            "external_id": str(raw.get("id")),
            "source": self.provider_name,
            "title": title.strip(),
            "company": raw.get("company", {}).get("display_name", "Adzuna Employer") if isinstance(raw.get("company"), dict) else "Adzuna Employer",
            "location": display_name,
            "city": display_name.split(",")[0].strip() if "," in display_name else display_name,
            "country": "UK",
            "remote": "remote" in display_name.lower(),
            "hybrid": False,
            "employment_type": "Full-time",
            "job_category": raw.get("category", {}).get("label", "IT Jobs") if isinstance(raw.get("category"), dict) else "IT Jobs",
            "experience_level": "Mid-Level",
            "salary_min": raw.get("salary_min"),
            "salary_max": raw.get("salary_max"),
            "salary_currency": "GBP",
            "salary_range": f"£{int(raw.get('salary_min'))} - £{int(raw.get('salary_max'))}" if raw.get("salary_min") and raw.get("salary_max") else "Salary Not Disclosed",
            "description": raw.get("description", title),
            "skills": ["Software Engineering", "SQL", "Cloud", "Agile"],
            "posted_at": posted_at,
            "apply_url": apply_url,
            "source_url": apply_url,
            "is_active": True,
            "raw_data": raw
        }

class SeedJobProvider(JobProvider):
    """Seed / Fallback Provider ensuring robust 0-14 day job opportunities across all categories"""
    @property
    def provider_name(self) -> str:
        return "Company Careers"

    async def fetch_jobs(self, query: str = "Software", location: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        seeds = [
            # TODAY (0 days ago) - Indian Tech Hubs & Global Giants
            {
                "id": "seed-in-101",
                "title": "Senior AI & Machine Learning Engineer",
                "company": "Swiggy",
                "location": "Bengaluru, Karnataka, India (Hybrid)",
                "city": "Bengaluru",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Senior",
                "category": "AI / ML",
                "salary_min": 3000000,
                "salary_max": 4800000,
                "salary_currency": "INR",
                "salary_range": "₹30,00,000 - ₹48,00,000",
                "description": "Architect hyper-personalized recommendation algorithms, delivery route optimization models, and real-time demand forecasting ML systems.",
                "skills": ["Python", "PyTorch", "Spark", "Kubernetes", "Kafka", "Machine Learning", "System Design"],
                "required_skills": ["Python", "PyTorch", "Spark", "Kafka"],
                "preferred_skills": ["Kubernetes", "System Design"],
                "posted_at": now - timedelta(hours=2),
                "apply_url": "https://careers.swiggy.com",
                "source": "Company Careers"
            },
            {
                "id": "seed-in-102",
                "title": "Backend Engineering Manager / Lead",
                "company": "Razorpay",
                "location": "Bengaluru, Karnataka, India (Hybrid)",
                "city": "Bengaluru",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Senior",
                "category": "Backend",
                "salary_min": 3500000,
                "salary_max": 5500000,
                "salary_currency": "INR",
                "salary_range": "₹35,00,000 - ₹55,00,000",
                "description": "Lead payment gateway core infrastructure handling millions of daily transactions across UPI, card networks, and banking APIs.",
                "skills": ["Go", "Java", "Microservices", "PostgreSQL", "Redis", "Distributed Systems", "AWS"],
                "required_skills": ["Go", "Java", "Microservices", "PostgreSQL"],
                "preferred_skills": ["Redis", "Distributed Systems", "AWS"],
                "posted_at": now - timedelta(hours=4),
                "apply_url": "https://razorpay.com/jobs",
                "source": "Lever"
            },
            {
                "id": "seed-in-103",
                "title": "Full-Stack Software Engineer (Vue 3 / Python)",
                "company": "Flipkart",
                "location": "Bengaluru, Karnataka, India",
                "city": "Bengaluru",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Mid Level",
                "salary_min": 2200000,
                "salary_max": 3500000,
                "salary_currency": "INR",
                "salary_range": "₹22,00,000 - ₹35,00,000",
                "description": "Develop high-scale e-commerce frontend seller dashboards and resilient search index microservices.",
                "skills": ["Vue.js", "JavaScript", "Python", "FastAPI", "PostgreSQL", "TailwindCSS"],
                "required_skills": ["Vue.js", "Python", "JavaScript"],
                "preferred_skills": ["FastAPI", "TailwindCSS"],
                "posted_at": now - timedelta(hours=6),
                "apply_url": "https://www.flipkartcareers.com",
                "source": "Company Careers"
            },
            {
                "id": "seed-101",
                "title": "Machine Learning Engineer",
                "company": "OpenAI",
                "location": "San Francisco, CA (Hybrid)",
                "city": "San Francisco",
                "country": "USA",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Mid Level",
                "category": "AI / ML",
                "salary_min": 180000,
                "salary_max": 260000,
                "salary_currency": "USD",
                "salary_range": "$180,000 - $260,000",
                "description": "Architect and scale distributed deep learning model training pipelines, LLM inference infrastructure, and evaluation benchmarks.",
                "skills": ["Python", "PyTorch", "CUDA", "LLMs", "Distributed Systems", "Docker", "Kubernetes"],
                "required_skills": ["Python", "PyTorch", "CUDA", "LLMs"],
                "preferred_skills": ["Distributed Systems", "Kubernetes", "Ray"],
                "posted_at": now - timedelta(hours=4),
                "apply_url": "https://openai.com/careers",
                "source": "Ashby"
            },
            # YESTERDAY (1 day ago) - India & Global
            {
                "id": "seed-in-104",
                "title": "Software Development Engineer II (SDE-2)",
                "company": "Amazon India",
                "location": "Hyderabad, Telangana, India",
                "city": "Hyderabad",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Mid Level",
                "category": "Software Development",
                "salary_min": 2800000,
                "salary_max": 4200000,
                "salary_currency": "INR",
                "salary_range": "₹28,00,000 - ₹42,00,000",
                "description": "Design high-availability cloud services for Amazon Fulfillment and Logistics tech stack in Hyderabad Development Center.",
                "skills": ["Java", "Spring Boot", "AWS", "DynamoDB", "System Design", "Distributed Systems"],
                "required_skills": ["Java", "Spring Boot", "AWS"],
                "preferred_skills": ["DynamoDB", "System Design"],
                "posted_at": now - timedelta(days=1, hours=2),
                "apply_url": "https://www.amazon.jobs/en/locations/hyderabad-india",
                "source": "Company Careers"
            },
            {
                "id": "seed-in-105",
                "title": "Frontend Engineer (React / TypeScript)",
                "company": "Zomato",
                "location": "Gurugram, Haryana, India",
                "city": "Gurugram",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Mid Level",
                "category": "Frontend",
                "salary_min": 1800000,
                "salary_max": 2800000,
                "salary_currency": "INR",
                "salary_range": "₹18,00,000 - ₹28,00,000",
                "description": "Build dynamic, fast merchant portal web app interfaces using React, Next.js, Redux Toolkit, and WebSockets.",
                "skills": ["React", "TypeScript", "Next.js", "Redux", "CSS", "TailwindCSS"],
                "required_skills": ["React", "TypeScript", "Next.js"],
                "preferred_skills": ["Redux", "TailwindCSS"],
                "posted_at": now - timedelta(days=1, hours=5),
                "apply_url": "https://www.zomato.com/careers",
                "source": "Greenhouse"
            },
            {
                "id": "seed-102",
                "title": "Senior Full-Stack & Flutter Developer",
                "company": "Ramp",
                "location": "Remote (US / India)",
                "city": "Remote",
                "country": "Global",
                "remote": True,
                "hybrid": False,
                "employment_type": "Full-time",
                "experience_level": "Senior",
                "category": "Full Stack",
                "salary_min": 160000,
                "salary_max": 220000,
                "salary_currency": "USD",
                "salary_range": "$160,000 - $220,000",
                "description": "Build high-throughput financial web and mobile applications using Vue 3, FastAPI, Flutter, and PostgreSQL.",
                "skills": ["Python", "FastAPI", "Vue.js", "Flutter", "PostgreSQL", "TailwindCSS", "System Design"],
                "required_skills": ["Python", "FastAPI", "Vue.js", "PostgreSQL"],
                "preferred_skills": ["Flutter", "TailwindCSS", "Docker"],
                "posted_at": now - timedelta(hours=8),
                "apply_url": "https://ramp.com/careers",
                "source": "Ashby"
            },
            {
                "id": "seed-103",
                "title": "AI Research Scientist Intern",
                "company": "Anthropic",
                "location": "San Francisco, CA",
                "city": "San Francisco",
                "country": "USA",
                "remote": False,
                "hybrid": True,
                "employment_type": "Internship",
                "experience_level": "Internship",
                "category": "AI / ML",
                "salary_min": 100000,
                "salary_max": 140000,
                "salary_currency": "USD",
                "salary_range": "$100,000 - $140,000",
                "description": "Conduct frontier AI alignment and mechanistic interpretability research alongside core Anthropic safety teams.",
                "skills": ["Python", "PyTorch", "Machine Learning", "Linear Algebra", "NLP", "Transformers"],
                "required_skills": ["Python", "PyTorch", "Machine Learning"],
                "preferred_skills": ["NLP", "Transformers"],
                "posted_at": now - timedelta(hours=14),
                "apply_url": "https://anthropic.com/careers",
                "source": "Greenhouse"
            },
            # 2 DAYS AGO - India & Global
            {
                "id": "seed-in-106",
                "title": "Cloud DevOps & Site Reliability Engineer",
                "company": "CRED",
                "location": "Bengaluru, Karnataka, India",
                "city": "Bengaluru",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Mid Level",
                "category": "DevOps",
                "salary_min": 2400000,
                "salary_max": 3800000,
                "salary_currency": "INR",
                "salary_range": "₹24,00,000 - ₹38,00,000",
                "description": "Manage multi-region Kubernetes clusters, Terraform infrastructure-as-code, zero-downtime deployment pipelines, and observability stack.",
                "skills": ["DevOps", "Kubernetes", "Docker", "Terraform", "AWS", "Prometheus", "Grafana"],
                "required_skills": ["Kubernetes", "Docker", "Terraform", "AWS"],
                "preferred_skills": ["Prometheus", "Grafana"],
                "posted_at": now - timedelta(days=2, hours=3),
                "apply_url": "https://cred.club/careers",
                "source": "Company Careers"
            },
            {
                "id": "seed-in-107",
                "title": "Data Analyst (Analytics & Growth)",
                "company": "PhonePe",
                "location": "Bengaluru, Karnataka, India",
                "city": "Bengaluru",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Junior",
                "category": "Data Analyst",
                "salary_min": 1400000,
                "salary_max": 2200000,
                "salary_currency": "INR",
                "salary_range": "₹14,00,000 - ₹22,00,000",
                "description": "Analyze merchant funnel metrics, transaction success rates, SQL cohort retention, and build automated Tableau executive dashboards.",
                "skills": ["SQL", "Python", "Tableau", "Pandas", "Statistics", "Excel"],
                "required_skills": ["SQL", "Python", "Tableau"],
                "preferred_skills": ["Pandas", "Statistics"],
                "posted_at": now - timedelta(days=2, hours=7),
                "apply_url": "https://www.phonepe.com/careers",
                "source": "Company Careers"
            },
            {
                "id": "seed-104",
                "title": "Data Analyst (Finance & Strategy)",
                "company": "Spotify",
                "location": "New York, NY (Hybrid)",
                "city": "New York",
                "country": "USA",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Junior",
                "category": "Data Analyst",
                "salary_min": 110000,
                "salary_max": 145000,
                "salary_currency": "USD",
                "salary_range": "$110,000 - $145,000",
                "description": "Analyze key user subscription metrics, revenue churn modeling, SQL cohort analysis, and Tableau dashboard executive reporting.",
                "skills": ["SQL", "Python", "Tableau", "Pandas", "Statistics", "Excel", "Data Visualization"],
                "required_skills": ["SQL", "Python", "Tableau"],
                "preferred_skills": ["Pandas", "Statistics"],
                "posted_at": now - timedelta(days=1, hours=3),
                "apply_url": "https://spotifyjobs.com",
                "source": "Lever"
            },
            {
                "id": "seed-105",
                "title": "Backend Engineering Intern",
                "company": "Linear",
                "location": "Remote (Global / India)",
                "city": "Remote",
                "country": "Global",
                "remote": True,
                "hybrid": False,
                "employment_type": "Internship",
                "experience_level": "Fresher",
                "category": "Backend",
                "salary_min": 80000,
                "salary_max": 105000,
                "salary_currency": "USD",
                "salary_range": "$80,000 - $105,000",
                "description": "Develop high-performance sync engines and real-time GraphQL APIs using TypeScript, Node.js, and PostgreSQL.",
                "skills": ["TypeScript", "Node.js", "GraphQL", "PostgreSQL", "Redis", "Git"],
                "required_skills": ["TypeScript", "Node.js", "GraphQL"],
                "preferred_skills": ["PostgreSQL", "Redis"],
                "posted_at": now - timedelta(days=1, hours=8),
                "apply_url": "https://linear.app/careers",
                "source": "Ashby"
            },
            # 3 DAYS AGO - India & Global
            {
                "id": "seed-in-108",
                "title": "Cybersecurity & SOC Analyst",
                "company": "TCS (Tata Consultancy Services)",
                "location": "Mumbai / Pune, India",
                "city": "Mumbai",
                "country": "India",
                "remote": False,
                "hybrid": True,
                "employment_type": "Full-time",
                "experience_level": "Mid Level",
                "category": "Cybersecurity",
                "salary_min": 1000000,
                "salary_max": 1800000,
                "salary_currency": "INR",
                "salary_range": "₹10,00,000 - ₹18,00,000",
                "description": "Perform enterprise SIEM monitoring, threat intelligence analysis, vulnerability scanning, and incident response for global clients.",
                "skills": ["Cybersecurity", "SIEM", "Python", "Network Security", "Incident Response", "Linux"],
                "required_skills": ["Cybersecurity", "SIEM", "Incident Response"],
                "preferred_skills": ["Python", "Linux"],
                "posted_at": now - timedelta(days=3, hours=4),
                "apply_url": "https://www.tcs.com/careers",
                "source": "Company Careers"
            },
            {
                "id": "seed-106",
                "title": "Cloud DevOps & Infrastructure Engineer",
                "company": "Cloudflare",
                "location": "Austin, TX (Remote)",
                "city": "Austin",
                "country": "USA",
                "remote": True,
                "hybrid": False,
                "employment_type": "Full-time",
                "experience_level": "Mid Level",
                "category": "DevOps",
                "salary_min": 140000,
                "salary_max": 185000,
                "salary_currency": "USD",
                "salary_range": "$140,000 - $185,000",
                "description": "Manage multi-region Kubernetes clusters, Terraform infrastructure-as-code, CI/CD pipelines, and edge network routing.",
                "skills": ["DevOps", "Kubernetes", "Docker", "Terraform", "AWS", "Go", "CI/CD"],
                "required_skills": ["Kubernetes", "Docker", "Terraform"],
                "preferred_skills": ["AWS", "Go", "CI/CD"],
                "posted_at": now - timedelta(days=2, hours=5),
                "apply_url": "https://cloudflare.com/careers",
                "source": "Greenhouse"
            },
            # 7 DAYS AGO
            {
                "id": "seed-109",
                "title": "Senior Frontend Engineer (Vue / Nuxt)",
                "company": "GitLab",
                "location": "Remote (Global / India)",
                "city": "Remote",
                "country": "Global",
                "remote": True,
                "hybrid": False,
                "employment_type": "Full-time",
                "experience_level": "Senior",
                "category": "Frontend",
                "salary_min": 150000,
                "salary_max": 200000,
                "salary_currency": "USD",
                "salary_range": "$150,000 - $200,000",
                "description": "Lead core UI component development in Vue 3, Pinia, TypeScript, and micro-frontend architecture for DevOps workflows.",
                "skills": ["Vue.js", "TypeScript", "JavaScript", "Pinia", "CSS", "TailwindCSS", "Jest"],
                "required_skills": ["Vue.js", "TypeScript", "JavaScript"],
                "preferred_skills": ["Pinia", "TailwindCSS"],
                "posted_at": now - timedelta(days=7, hours=2),
                "apply_url": "https://about.gitlab.com/jobs",
                "source": "Greenhouse"
            },
            # 12 DAYS AGO
            {
                "id": "seed-110",
                "title": "Apprentice Software Developer",
                "company": "Shopify",
                "location": "Toronto, Canada (Hybrid)",
                "city": "Toronto",
                "country": "Canada",
                "remote": False,
                "hybrid": True,
                "employment_type": "Apprenticeship",
                "experience_level": "Fresher",
                "category": "Software Development",
                "salary_min": 65000,
                "salary_max": 85000,
                "salary_currency": "USD",
                "salary_range": "$65,000 - $85,000",
                "description": "Mentored 12-month software development program working on e-commerce APIs, Ruby on Rails backend, and React web apps.",
                "skills": ["Python", "JavaScript", "Ruby", "SQL", "Git", "HTML/CSS"],
                "required_skills": ["Python", "JavaScript", "SQL"],
                "preferred_skills": ["Ruby", "Git"],
                "posted_at": now - timedelta(days=12, hours=6),
                "apply_url": "https://shopify.com/careers",
                "source": "Company Careers"
            }
        ]
        return seeds

    def normalize_job(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return raw
