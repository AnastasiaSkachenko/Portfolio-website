import 'bootstrap/dist/css/bootstrap.min.css'
import { Row, Col} from 'react-bootstrap' 
import './App.css'
import { useEffect, useState } from 'react';
import axios from 'axios';
 

interface Project {
  name: string,
  description: string,
  tools: string[]
}

interface ProjectFetched {
  name: string,
  description: string,
  tools: string

}


function App() {
  const [projects, setProjects] = useState<Project[]>()
  const [name, setName] = useState<string>('')
  const [body, setBody] = useState<string>('')
  const [email, setEmail] = useState<string>('')
  const [success, setSuccess] = useState<string | null>(null)

  const getProjects = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/get-project/');
       const fetchedProjects = response.data.projects.map((project: ProjectFetched) => ({
        ...project,
        tools: project.tools.split(','), 
      }));
       setProjects(fetchedProjects);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };
  
  useEffect(() => {
    if (!projects?.[1]) {
      getProjects()
    }
  }, [projects])

  const sendEmail = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSuccess('sending...')
    try {
      await axios.post('http://127.0.0.1:8000/api/send-confirmation/', 
        {
          name,
          email,
          body
        }
      );
      setSuccess('I got your message!')
      setName('')
      setBody('')
      setEmail('')
    } catch (error) {
      console.error('Error sending message:', error);
    }  

  }

  useEffect(() => {
    const sections = document.querySelectorAll('.container');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');  
        }  
      });
    }, { threshold: 0.5 }); 

    sections.forEach((section) => {
      observer.observe(section);
    });

    return () => {
      sections.forEach((section) => {
        observer.unobserve(section);
      });
    };
  }, []);
 
  
  return (
    <>
      <section id="main"  className='-center' >
        <nav>
          <a href='#about-me'>About me</a>
          <a href='#contact' >Contact me</a>
        </nav>
        <div className="container p-md-0  mx-md-4 py-lg-5  ">
          <Row className="align-items-center   mb-md-5 ">
             <Col xs={12} md={7} lg={7} className="d-flex justify-content-center">
              <h3 className="display-4 display-md-5 justify-content-center fw-bold">Front-end Developer</h3>
            </Col>
            <Col xs={12} md={5} lg={5} className="d-flex justify-content-center pl-md-2 ">
              <div className="circle">
                <div className="circle-inner">
                  <img src="/static/images/me.PNG" alt="Profile" />
                </div>
              </div>
            </Col>
          </Row>
          <Row className="align-items-center  mt-5">
             <Col xs={12} md={7} lg={7} className="d-flex justify-content-center   gap-3">
              <a href="#skills" className="btn btn-4 btn-dark px-4 py-2">Skills</a>
              <a href="#projects" className="btn btn-4 btn-dark px-4 py-2">Projects</a>
            </Col>
            <Col xs={12} md={5} lg={5} className=" justify-content-center">
              <h3 className="text-center">I am Anastasiia Skachenko</h3>
            </Col>
          </Row>
        </div>

      </section>

      <section id='about-me' className="py-5">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-12 col-md-8 col-lg-6 text-center">
              <h3 className="display-4 mb-4">About Me</h3>
              <p className="lead">
                I am a Front-End Developer with 2 years of experience building applications using vanilla JavaScript and React.js. 
                I have developed user-friendly and visually appealing applications for industries such as beauty salons and restaurants. 
                While I specialize in front-end development, I have a strong foundation in web technologies, ensuring seamless integration 
                of responsive designs with back-end systems. 
              </p>


              <div className='row mt-5'>
                <div className='col-md-6 col-12 col-lg-6'> 
                    <a href="https://www.linkedin.com/in/anastasiia-skachenko/" target="_blank" rel="noopener noreferrer"  className="btn btn-dark py-2 px-4 w-40 mb-2" >LinkedIn</a>
                  </div>
                <div className='col-md-6 col-12 col-lg-6'> 
                  <a href="https://github.com/AnastasiaSkachenko" target="_blank" rel="noopener noreferrer" className="btn btn-dark py-2 px-4 w-40 mb-2" >GitHub</a>              
                </div>
                </div>
            </div>
          </div>
        </div>
      </section>

      <section id="projects" >
        <div className="container">
          <div className="row justify-content-center">
            <h3 className="display-4 mb-4 text-center">Projects</h3>

            {projects?.map((project) => (
              <div key={project.name} className="project-card mb-4 p-4">
                <h3>{project.name}</h3>
                <ul>
                  <li>{project.description}</li>
                  <li>Tools Used:</li>
                  <div className="d-flex justify-content-start gap-3">
                    {project.tools.map((tool) => (
                      <button key={tool} className="btn btn-outline-dark mb-2">{tool}</button>
                    ))}
                  </div>
                </ul>
              </div>
            
            ))}
            
 
          </div>
        </div>
      </section>


      <section id="skills" className="py-5">
      <div className="container">
        <div className="row justify-content-center">
          <h3 className="display-4 mb-4 text-center">Skills</h3>
          <div className="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4 justify-content-center">
            
            <div className="col">
              <div className="card text-center shadow border-light rounded-3">
                <img src="/static/images/python.png" alt="Python" className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                <div className="card-body">
                  <h6 className="card-title font-weight-bold">Python</h6>
                  <p className="card-text text-muted">4 years experience</p>
                </div>
              </div>
            </div>

            <div className="col">
              <div className="card text-center shadow border-light rounded-3">
                <img src="/static/images/django.png" alt="Django" className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                <div className="card-body">
                  <h6 className="card-title font-weight-bold">Django</h6>
                  <p className="card-text text-muted">3 years experience</p>
                </div>
              </div>
            </div>

            <div className="col">
              <div className="card text-center shadow border-light rounded-3">
                <img src="/static/images/html5.png" alt="HTML5" className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                <div className="card-body">
                  <h6 className="card-title font-weight-bold">HTML</h6>
                  <p className="card-text text-muted">2 years experience</p>
                </div>
              </div>
            </div>

            <div className="col">
              <div className="card text-center shadow border-light rounded-3">
                <img src="/static/images/js.jpeg" alt="JavaScript" className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                <div className="card-body">
                  <h6 className="card-title font-weight-bold">JavaScript</h6>
                  <p className="card-text text-muted">3 years experience</p>
                </div>
              </div>
            </div>

            <div className="col">
              <div className="card text-center shadow border-light rounded-3">
                <img src="/static/images/CSS3.png" alt="CSS3" className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                <div className="card-body">
                  <h6 className="card-title font-weight-bold">CSS3</h6>
                  <p className="card-text text-muted">2 years experience</p>
                </div>
              </div>
            </div>

            <div className="col">
              <div className="card text-center shadow border-light rounded-3">
                <img src="/static/images/react.png" alt="React" className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                <div className="card-body">
                  <h6 className="card-title font-weight-bold">React</h6>
                  <p className="card-text text-muted">1 year experience</p>
                </div>
              </div>
            </div>

            <div className="col">
              <div className="card text-center shadow border-light rounded-3">
                <img src="/static/images/bootstrap.png" alt="Bootstrap" className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                <div className="card-body">
                  <h6 className="card-title font-weight-bold">Bootstrap</h6>
                  <p className="card-text text-muted"> {'<'}1 year experience</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>


    <section id="contact" className=" py-5">
      <div className="container text-center">
        <h3 className="display-4 mb-4">Contact Me</h3>
        <p className="lead mb-4">Feel free to get in touch with me for collaboration, feedback, or just a friendly chat!</p>
        <div className="row justify-content-center">
          <div className="fields">
            <form  onSubmit={sendEmail}>
              <div className="mb-3">
                <label htmlFor="name" className="form-label">Your Name</label>
                <input type="text" className="form-control" id="name" name="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Enter your name" required />
              </div>
              <div className="mb-3">
                <label htmlFor="email" className="form-label">Your Email</label>
                <input type="email" className="form-control" id="email" name="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Enter your email" required />
              </div>
              <div className="mb-3">
                <label htmlFor="message" className="form-label">Your Message</label>
                <textarea className="form-control" id="message" name="message" value={body} onChange={(e) => setBody(e.target.value)} rows={4} placeholder="Write your message" required></textarea>
              </div>
              <div className="mb-3">
                <button type="submit" className="btn btn-dark btn-lg">Send Message</button>
              </div>
              {success && <p className='success'>{success}</p>}
            </form>
          </div>
        </div>
      </div>
    </section>

    <footer className="bg-dark text-white py-4">
      <div className="container text-center">
        <div className="row">
          <div className="col-md-4">
            <h5>Contact Me</h5>
            <ul className="list-unstyled">
              <li><strong>Email:</strong> <a href="mailto:company123workemail@gmail.com" className="text-white">skachenkkoa@gmail.com</a></li>
              <li><strong>Phone:</strong> <a href="tel:+123456789" className="text-white">+43 73 359 68 94</a></li>
            </ul>
          </div>
          <div className="col-md-4">
            <h5>Follow Me</h5>
            <ul className="list-unstyled">
              <li><a href="https://www.linkedin.com/in/anastasiia-skachenko/" target="_blank" rel="noopener noreferrer" className="text-white">LinkedIn</a></li>
              <li><a href="https://github.com/AnastasiaSkachenko" target="_blank" rel="noopener noreferrer" className="text-white">GitHub</a></li>
            </ul>
          </div>
          <div className="col-md-4"> 
            <a href="#main" className="btn btn-light">Go to Main Section</a>
          </div>
        </div>
      </div>
      <div className="text-center mt-3">
        <small>&copy; 2024 Anastasiia Skachenko. All rights reserved.</small>
      </div>
    </footer>

  </>
  )
}

export default App
