import 'bootstrap/dist/css/bootstrap.min.css'
import {Button, Row, Col} from 'react-bootstrap' 
import './App.css'


function App() {
 
  return (
    <>
      <section id="main">
        <nav>
          <a href='#about-me'>About me</a>
          <a href='#contact' >Contact me</a>
        </nav>
        <div className="container">
          <Row className="align-items-center mb-5">
            <Col xs={0} md={1} lg={1} ></Col>
            <Col xs={12} md={5} lg={7} className="text-center text-md-start">
              <h3 className="display-5 fw-bold">Front-end Developer</h3>
            </Col>
            <Col xs={12} md={6} lg={4} className="d-flex justify-content-center">
              <div className="circle">
                <div className="circle-inner">
                  <img src="./me.PNG" alt="Profile" />
                </div>
              </div>
            </Col>
          </Row>
          <Row className="align-items-center mt-5">
            <Col xs={0} md={2} lg={2} ></Col>
            <Col xs={12} md={4} lg={6} className="d-flex justify-content-center justify-content-md-start gap-3">
              <Button variant="outline-dark" size="lg">Skills</Button>
              <Button variant="outline-dark" size="lg">Projects</Button>
            </Col>
            <Col xs={12} md={6} lg={4} className="text-center">
              <h3 className="text-center">I am Anastasiia Skachenko</h3>
            </Col>
          </Row>
        </div>

      </section>

      <section id='about-me'>

      </section>

      <section id='projects'>

      </section>

      <section id='skills'>

      </section>
      <section id='contact'>

      </section>
    </>
  )
}

export default App
