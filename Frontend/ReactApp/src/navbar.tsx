import React, { useState } from 'react';

interface Section {
  id: string;
  label: string;
}

const Navbar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(true);

  const sections: Section[] = [
    { id: 'main', label: 'Main' },
    { id: 'about-me', label: 'About Me' },
    { id: 'projects', label: 'Projects' },
    { id: 'skills', label: 'Skills' },
    { id: 'contact', label: 'Contact Me' },
  ];

  const toggle = () => {
    setIsCollapsed(!isCollapsed); // Toggle the collapse state
  };

  const handleLinkClick = () => {
    setIsCollapsed(true); // Collapse the navbar when a link is clicked
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <div  >
        {/* Hamburger menu button */}
        <button
          onClick={toggle}
          className="toggler"
          type="button"
          aria-controls="navbarNav"
          aria-expanded={!isCollapsed ? 'true' : 'false'}
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Navbar Links */}
        <div className={`collapse navbar-collapse ${!isCollapsed ? 'show' : ''}`} id="navbarNav">
          <ul className="navbar-nav">
            {sections.map((section, index) => (
              <li key={index} className="nav-item">
                <a
                  className="nav-link-h"
                  href={"#" + section.id}
                  onClick={handleLinkClick} // Collapse navbar when link is clicked
                >
                  {section.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
