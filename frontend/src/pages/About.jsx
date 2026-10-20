
import PageTransition from "../components/common/PageTransition";

const technologies = [
  "Python",
  "Scikit-learn",
  "FastAPI",
  "MongoDB Atlas",
  "React",
  "Recharts",
  "Motion",
];

const contacts = [
  {
    name: "Gmail",
    href: "https://mail.google.com/mail/?view=cm&fs=1&to=aditya.menon2005%40gmail.com",
    label: "Email Aditya",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="m3 7 9 7 9-7" />
      </svg>
    ),
  },
  {
    name: "LinkedIn",
    href: "https://linkedin.com/in/aditya-menon-061169295",
    label: "Visit Aditya's LinkedIn profile",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6Z" />
        <rect x="2" y="9" width="4" height="12" />
        <circle cx="4" cy="4" r="2" />
      </svg>
    ),
  },
  {
    name: "GitHub",
    href: "https://github.com/adityamenon2205",
    label: "Visit Aditya's GitHub profile",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
      </svg>
    ),
  },
];

function About() {
  return (
    <PageTransition>
      <div className="about-page">
        <section className="dashboard-card about-card">
          <div className="about-section">
            <p className="eyebrow">THE PROJECT</p>
            <h1>About PL Predictor</h1>

            <p className="about-description">
              PL Predictor combines machine learning, football
              analytics, and interactive data visualisation to
              explore Premier League match outcomes. It uses
              historical match data and engineered performance
              features to generate predictions with probabilities,
              while an interactive dashboard makes team statistics,
              league trends, and prediction history easier to
              understand.
            </p>
          </div>

          <div className="about-section about-technologies">
            <p className="eyebrow">BUILT WITH</p>

            <div className="technology-list">
              {technologies.map((technology) => (
                <span
                  className="technology-badge"
                  key={technology}
                >
                  {technology}
                </span>
              ))}
            </div>
          </div>

          <div className="about-section about-contact">
            <h2>Let's connect</h2>

            <p className="about-contact-description">
              Have questions about the project or want to connect?
              Find me here.
            </p>

            <div className="contact-grid">
              {contacts.map((contact) => (
                <a
                  className="contact-card"
                  href={contact.href}
                  key={contact.name}
                  aria-label={contact.label}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span className="contact-icon">
                    {contact.icon}
                  </span>

                  <span className="contact-name">
                    {contact.name}
                  </span>
                </a>
              ))}
            </div>
          </div>
        </section>
      </div>
    </PageTransition>
  );
}

export default About;
