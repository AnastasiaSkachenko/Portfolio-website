import 'bootstrap/dist/css/bootstrap.min.css'
import { Row, Col} from 'react-bootstrap' 
import './App.css'
import { useEffect, useState } from 'react';
import axios from 'axios';
import Cookies from "universal-cookie"; 
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// 3B1E54 9B7EBD D4BEE4 EEEEEE

interface Project {
  name: string,
  description: string,
  tools: string[]
}

interface Skill {
  name: string,
  image: string,
  experience: number
}

interface ProjectFetched {
  name: string,
  description: string,
  tools: string

}


function App() {
  const [projects, setProjects] = useState<Project[]>()
  const [skills, setSkills] = useState<Skill[]>()
  const [name, setName] = useState<string>('')
  const [body, setBody] = useState<string>('')
  const [email, setEmail] = useState<string>('')
  const [success, setSuccess] = useState<string | null>(null)


  const production = false
  const imageRoot =  production ? '/static/images/' : './images/'
  const baseUrl = production? window.location.origin : 'http://127.0.0.1:8000';

  const cookies = new Cookies()


  const axiosInstance = axios.create({
    headers: {
        'X-CSRFToken': cookies.get("csrftoken")
    }
  });


  useEffect(() => {
    const getProjects = async () => { 
      try {
        const response = await axiosInstance.get(`${baseUrl}/api/get-project/`);
        const fetchedProjects = response.data.projects.map((project: ProjectFetched) => ({
          ...project,
          tools: project.tools.split(','), 
        }));
        setProjects(fetchedProjects);
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    };
    
    const getSkills = async () => { 
      try {
        const response = await axiosInstance.get(`${baseUrl}/api/get-skill/`);
        const fetchedSkills = response.data.skills
        setSkills(fetchedSkills);
      } catch (error) {
        console.error('Error fetching skills:', error);
      }
    };


    if (!projects?.[1]) {
      getProjects()
    }

    if (!skills?.[1]) {
      getSkills()
    }
  }, [projects, skills, axiosInstance, baseUrl])

  const sendEmail = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const baseUrl = window.location.origin;
    setSuccess('sending...')
    try {
      await axiosInstance.post(`${baseUrl}/api/send-confirmation/`, 
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
    }, { threshold: 0.1 }); 

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
      <section id="main"   >
        <nav>
          <a className='nav-link' href='#about-me'>About me</a>
          <a className='nav-link' href='#contact' >Contact me</a>
        </nav>
        <div className="container p-0  m-0 p-lg-5  ">
          <Row className="align-items-center  text-sm-center">
             <Col xs={12} md={12} lg={7} className='text-center pl-5' >
                <Row >
                  <h1  className=" m-0   p-0   fw-bold">Anastasiia Skachenko</h1>
                </Row>
                <Row >
                  <h3 className=" p-0   ">Front-end Developer</h3>
                </Row>

             </Col>
            <Col xs={12} md={12} lg={5} className="d-flex justify-content-center  pl-5 pl-md-2 ">
               <Row className='justify-content-center'>
                <div className="circle">
                  <div className="circle-inner">
                    <img src={`${imageRoot}/me.PNG`} alt="Profile" />
                  </div>
                </div>
              </Row>

            </Col>
          </Row>
          <Row className="align-items-center justify-content-center  mt-3">
             <Col   className="d-flex justify-content-center   gap-3">
              <a href="#skills" className="btn btn-4 btn-dark px-4 py-2">Skills</a>
              <a href="#projects" className="btn btn-4 btn-dark px-4 py-2">Projects</a>
            </Col>
          </Row>
        </div>

      </section>

      <section id='about-me' className="py-5 d-flex  align-items-center">
        <div className="container ">
          <div  >
            <div className="col-12 col-md-8 col-lg-6 text-center">
              <h1 className=" mb-4">About Me</h1>
              <p className="lead">
                I am a Front-End Developer with 2 years of experience building applications using vanilla JavaScript and React.js. 
                I have developed user-friendly and visually appealing applications for industries such as beauty salons and restaurants. 
                While I specialize in front-end development, I have a strong foundation in web technologies, ensuring seamless integration 
                of responsive designs with back-end systems. 
              </p>


              <div className='d-flex flex-row gap-5 justify-content-center mt-5'>
                <a href="http://linkedin.com/in/anastasiia-skachenko" target="_blank" rel="noopener noreferrer" className="text-violet">
                  <img src={imageRoot + 'linkedIn.png'}/>
                </a>
                <a href="https://github.com/AnastasiaSkachenko" target="_blank" rel="noopener noreferrer" className="text-white">
                  <img src={imageRoot + 'github.png'}/>
                </a>              
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="projects" className='d-flex  align-items-center'>
        <div className="container">
          <div >
            <h1 className=" mb-4 text-center">Projects</h1>
            <div id="carouselProjects" className="carousel slide" data-bs-ride="carousel" data-bs-touch="true">
              <div className="carousel-indicators">
                {projects?.map((_, index) => (
                  <button
                    key={index}
                    type="button"
                    data-bs-target="#carouselProjects"
                    data-bs-slide-to={index}
                    className={index === 0 ? "active" : ""}
                    aria-current={index === 0 ? "true" : undefined}
                    aria-label={`Slide ${index + 1}`}
                  ></button>
                ))}
              </div>

              <div className="carousel-inner">
                {projects?.map((project, index) => (
                  <div key={project.name} className={`carousel-item ${index === 0 ? "active" : ""}`}>
                    <div className="project-card p-4">
                      <h3>{project.name}</h3>
                      <p>{project.description}</p>
                      <p className="fw-bold">Tools Used:</p>
                      <div className="d-flex flex-wrap gap-2">
                        {project.tools.map((tool) => (
                          <button key={tool} className="btn btn-outline-dark disabled-black mb-2" disabled>
                            {tool}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button
                className="carousel-control-prev   d-none d-sm-block"
                type="button"
                data-bs-target="#carouselProjects"
                data-bs-slide="prev"
              >
                <span className="carousel-control-prev-icon" aria-hidden="true"></span>
                <span className="visually-hidden">Previous</span>
              </button>

              <button
                className="carousel-control-next"
                type="button"
                data-bs-target="#carouselProjects"
                data-bs-slide="next"
              >
                <span className="carousel-control-next-icon d-none d-sm-block" aria-hidden="true"></span>
                <span className="visually-hidden">Next</span>
              </button>
            </div>
          </div>
        </div>
      </section>


      <section id="skills" className="py-5 d-flex  align-items-center">
      <div className="container">
        <div className="row justify-content-center">
          <h1 className="  mb-4 text-center">Skills</h1>
 

          <div className="media-scroller d-grid snaps-inline  gap-3 gap-xs-1">
            {skills?.map((skill) => (
              <div  key={skill.name} className="media-element d-grid p-4 px-5  text-center  shadow   rounded-3">
                  <img src={imageRoot + skill.image} alt={skill.name} className="card-img-top" style={{ height: '35px', objectFit: 'contain' }} />
                  <div className="card-body">
                    <p className="card-title fw-bold">{skill.name}</p>
                    <p className="card-text text-muted ">{skill.experience + (skill.experience > 1 ? ' years' : ' year')} of experience</p>
                  </div>
              </div>

            ))}

          </div>
        </div>
      </div>
    </section>


    <section id="contact" className=" py-5 d-flex  align-items-center">
      <div className="container text-center">
        <h1 className='mb-0' >Contact Me</h1>
        <p className="lead mb-0 ">Feel free to get in touch with me for collaboration, feedback, or just a friendly chat!</p>
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
                <button type="submit" className="btn btn-dark ">Send Message</button>
              </div>
              {success && <p className='success'>{success}</p>}
            </form>
          </div>
        </div>
      </div>
    </section>

    <footer className="text-violet py-3 py-sm-4 py-md-5 ">
      <div className="container text-center">
      <div className="row">
        <div className="col-12 col-sm-6">
          <h5 className='fw-bold'>Contact Me</h5>
          <ul className="list-unstyled">
            <li><strong className="text-violet">Email:</strong> <a href="mailto:skachenkoa@gmail.com" className="text-violet">skachenkkoa@gmail.com</a></li>
            <li><strong className="text-violet">Phone:</strong> <a href="tel:+123456789" className="text-violet">+43 73 359 68 94</a></li>
          </ul>
        </div>
        <div className="col-12 col-sm-6  ">
          <h5 className='fw-bold d-none d-sm-block'>Follow Me</h5>
          <ul className="list-unstyled d-flex align-items-center justify-content-center mt-0 mt-sm-3">
            <li><a href="http://linkedin.com/in/anastasiia-skachenko" target="_blank" rel="noopener noreferrer" className="text-violet">
              <img src={imageRoot + 'linkedIn.png'} alt="LinkedIn"/>
            </a></li>
            <li><a href="https://github.com/AnastasiaSkachenko" target="_blank" rel="noopener noreferrer" className="text-white">
              <img src={imageRoot + 'github.png'} alt="GitHub"/>
            </a></li>
          </ul>
        </div>
      </div>
      </div>
      <div className="text-center">
        <small>&copy; 2024 Anastasiia Skachenko. All rights reserved.</small>
      </div>
    </footer>

  </>
  )
}

export default App
