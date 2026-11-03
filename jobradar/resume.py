"""Resume and LinkedIn intake and local matching.
All data stays strictly on the user's computer. No cloud calls or uploads.
"""
import re, pathlib

COMMON_SKILLS = [
    # Programming & Frameworks
    "python", "javascript", "typescript", "java", "golang", "go", "c++", "c#", ".net", "php",
    "rust", "ruby", "swift", "kotlin", "scala", "react", "react native", "next.js", "vue",
    "angular", "node.js", "nodejs", "django", "fastapi", "flask", "spring", "spring boot",
    "laravel", "express",
    # Databases & Cloud/DevOps
    "sql", "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
    "docker", "kubernetes", "k8s", "ci/cd", "git", "github", "gitlab", "linux", "nginx",
    "rabbitmq", "graphql", "rest api", "microservices", "aws", "gcp", "azure",
    # Design & Product
    "figma", "adobe xd", "sketch", "ui/ux", "ui design", "ux design", "wireframing",
    "prototyping", "design system", "user research", "product management", "scrum", "agile",
    "jira", "confluence",
    # Data & AI
    "machine learning", "deep learning", "nlp", "pandas", "numpy", "tensorflow", "pytorch",
    "data analysis", "power bi", "tableau",
    # QA & Testing
    "software testing", "manual testing", "automation testing", "selenium", "cypress",
    "playwright", "postman", "unit testing", "integration testing", "qa",
    # Persian skill terms
    "پایتون", "جاوای اسکریپت", "تایپ‌اسکریپت", "ری‌اکت", "داکر", "کوبرنتیز", "گیت", "لینوکس",
    "تست نرم‌افزار", "کنترل کیفیت", "طراحی محصول", "طراحی رابط کاربری", "تجربه کاربری",
    "مدیریت محصول", "تحلیل داده", "هوش مصنوعی", "اسکرام", "اجایل"
]


def read_text_from_file(path_str):
    """Read plain text from a file. Handles .txt, .md, and optionally .pdf if pypdf is installed."""
    p = pathlib.Path(path_str).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    suffix = p.suffix.lower()
    if suffix in (".txt", ".md", ".markdown", ".json"):
        return p.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(p))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if text.strip():
                return text
        except ImportError:
            pass
        # Fallback if pypdf not installed or produced empty string
        raise ValueError(f"Reading PDF '{p.name}' requires 'pypdf'. Run: pip install pypdf, or provide resume as .txt / .md")
    else:
        # Default try utf-8
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            raise ValueError(f"Could not read format {suffix}: {e}")


def extract_skills(text, custom_skills=None):
    """Extract known technical/product skills and user custom skills from text."""
    if not text:
        return []
    s_lower = text.lower()
    found = []
    pool = list(custom_skills or []) + COMMON_SKILLS
    for sk in pool:
        sk_clean = sk.strip().lower()
        if not sk_clean or len(sk_clean) < 2:
            continue
        # match whole word/phrase
        escaped = re.escape(sk_clean)
        pattern = r"(?<![a-z0-9\u0600-\u06ff])" + escaped + r"(?![a-z0-9\u0600-\u06ff])"
        if re.search(pattern, s_lower):
            if sk_clean not in found:
                found.append(sk_clean)
    return found


def normalize_linkedin_url(val):
    """Validate or extract clean LinkedIn URL."""
    val = (val or "").strip()
    if not val:
        return ""
    if not val.startswith("http"):
        if "linkedin.com" in val:
            val = "https://" + val
        else:
            val = f"https://www.linkedin.com/in/{val.strip('/')}/"
    return val
