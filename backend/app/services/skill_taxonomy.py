"""Curated keyword lists used to detect and categorize skills mentioned in a resume.

Deliberately simple keyword matching (not NLP/AI) — transparent, deterministic, and
easy to extend. Matching is case-insensitive and word-boundary-aware so "Go" doesn't
match inside "Google", etc.
"""

PROGRAMMING_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Rust",
    "Kotlin", "Swift", "PHP", "Ruby", "Scala", "R", "MATLAB", "Perl", "Dart", "Lua",
    "Bash", "Shell", "SQL", "HTML", "CSS",
]

FRONTEND = [
    "React", "React.js", "Angular", "Vue", "Vue.js", "Next.js", "Nuxt.js", "Svelte",
    "Redux", "jQuery", "Bootstrap", "Tailwind CSS", "Tailwind", "Sass", "Material UI",
    "Chakra UI", "Webpack", "Vite",
]

BACKEND = [
    "Node.js", "Node", "Express", "Express.js", "FastAPI", "Django", "Flask",
    "Spring", "Spring Boot", "Laravel", "Ruby on Rails", "ASP.NET", ".NET",
    "GraphQL", "REST", "REST API", "gRPC", "Nest.js", "Nestjs",
]

DATABASE = [
    "MongoDB", "MySQL", "PostgreSQL", "Postgres", "SQLite", "Redis", "Oracle",
    "SQL Server", "Cassandra", "DynamoDB", "Firebase", "Firestore", "MariaDB",
    "Elasticsearch", "Supabase",
]

TOOLS = [
    "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "Jenkins", "CI/CD",
    "AWS", "Azure", "GCP", "Google Cloud", "Linux", "Postman", "Jira", "Figma",
    "Terraform", "Ansible", "Nginx", "Vercel", "Netlify", "Heroku",
]

SKILL_CATEGORIES: dict[str, list[str]] = {
    "programming": PROGRAMMING_LANGUAGES,
    "frontend": FRONTEND,
    "backend": BACKEND,
    "database": DATABASE,
    "tools": TOOLS,
}
