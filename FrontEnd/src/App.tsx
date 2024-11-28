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
        <div className='container'>

        <Row className="row-my">
          <Col  className='col-1'  xs={12} md={6} lg={8}>
            <h3>FrontEnd Developer</h3>
          </Col>
          <Col className="col-photo" xs={12} md={6} lg={4}>
            <div className="circle">
              <div className="circle-inner">
                <img src="./me.PNG" alt="Profile" />
              </div>
            </div>
          </Col>
        </Row>
        <Row className="row-my">
          <Col className='col-1'  xs={12} md={6} lg={8}>
            <Button className='button-my'>Skills</Button>
            <Button className='button-my'>Projects</Button>
          </Col>
          <Col  className='col-1' xs={12} md={6} lg={4}>
            <h3>I am Anastasiia Skachenko</h3>
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
