import React from 'react';
import './Footer.css';
import moderateLogo from '../assets/moderate-logo-white.png';
import euFlag from '../assets/eu-flag.jpg';
import iveLogo from '../assets/ive-logo.png';
import cticLogo from '../assets/ctic-logo-white.webp';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-top">

        <div className="footer-col">
          <a href="https://moderate-project.eu">
            <img
              src={moderateLogo}
              alt="MODERATE logo"
              className="footer-logo"
            />
          </a>
        </div>

        <div className="footer-col">
          <img
            src={euFlag}
            alt="European Union"
            className="footer-logo"
          />
        </div>

        <div className="footer-col">
          <a href="https://www.five.es" target="_blank" rel="noopener noreferrer">
            <img
              src={iveLogo}
              style={{ filter: "brightness(0) invert(1)" }}
              alt="IVE"
              className="footer-logo footer-logo-ive"
            />
          </a>
        </div>

        <div className="footer-col">
          <a href="https://www.fundacionctic.org" target="_blank" rel="noopener noreferrer">
            <img
              className="footer-logo footer-logo-ctic"
              src={cticLogo}
              alt="Fundacion CTIC"
            />
          </a>
        </div>


        <p className="footer-text"><i>
          Horizon Europe research and innovation programme under grant agreement No 101069834. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or CINEA. Neither the European Union nor the granting authority can be held responsible for.
        </i></p>

      </div>

      <div className="footer-bottom">
        <p>© 2025 MODERATE</p>
      </div>
    </footer>
  );
};

export default Footer;
