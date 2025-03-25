import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-top">

        <div className="footer-col">
          <a href="https://moderate-project.eu">
            <img
              src="https://moderate-project.eu/wp-content/uploads/2022/10/V2-White-300x68.png"
              alt="MODERATE logo"
            //   width="300"
            //   height="68"
            />
          </a>
          {/* <p className="footer-text">
            Horizon Europe research and innovation programme under grant agreement No 101069834. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or CINEA. Neither the European Union nor the granting authority can be held responsible for.
          </p> */}
        </div>

        <div className="footer-col">
          <img
            src="https://moderate-project.eu/wp-content/uploads/2022/10/normal-reproduction-high-resolution-1536x1024.jpg"
            alt="European Union"
            className="footer-img"
          />
        </div>

        <div className="footer-col">
          <img
            src="https://www.fundacionctic.org/sites/default/files/inline-images/logoblancocabecera.png"
            alt="Fundacion CTIC"
          // className="footer-img"
          />
        </div>

        <div className="footer-col">
          <img
            // className="footer-img"
            // src="https://www.five.es/wp-content/uploads/GVA-IVE_2025.svg"
            src="https://www.fiebdc.es/web2/datos/uploads/IVE-logo-500x500-1-500x321.png"
            style={{ filter: "brightness(0) invert(1)", width: "70%" }}
            alt="IVE"
          // className="footer-img"
          />
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
