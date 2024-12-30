import React, { useEffect, useState } from 'react';

interface Section {
  id: string;
  label: string;
}

const Sidebar: React.FC = () => {
  const sections: Section[] = [
    { id: 'main', label: 'Main' },
    { id: 'about-me', label: 'About Me' },
    { id: 'projects', label: 'Projects' },
    { id: 'skills', label: 'Skills' },
    { id: 'contact', label: 'Contact Me' },
  ];

  const [activeSection, setActiveSection] = useState<string>('');
 
  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, sectionId: string): void => {
    e.preventDefault();
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
      targetSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

 
 
  useEffect(() => {
    const sectionElements = document.querySelectorAll('section');

    const observerOptions: IntersectionObserverInit = {
      root: null, // Observing relative to the viewport
      threshold: 0.5, // 50% of the section must be visible
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const sectionId = entry.target.id;
        const link = document.querySelector(`.nav-link[data-section='${sectionId}']`);

        if (entry.isIntersecting) {
          setActiveSection(sectionId);
          if (link) {
            link.classList.add('active');
          }
        } else {
          if (link) {
            link.classList.remove('active');
          }
        }
      });
    }, observerOptions);

    sectionElements.forEach((section) => observer.observe(section));

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
  
      <nav className="sidebar">
        <ul className="nav d-flex flex-column justify-content-around">
          {sections.map((section) => (
            <li key={section.id} className="nav-item">
              <a
                className={`nav-link align-text-center text-violet ${activeSection === section.id ? 'active' : ''}`}
                href={`#${section.id}`}
                data-section={section.id}
                onClick={(e) => handleNavClick(e, section.id)}
              >
                {section.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    
  );
};

export default Sidebar;
