import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import {Row, Col, Toast, ToastContainer } from 'react-bootstrap';
import './App.css'
import { useEffect, useState } from 'react';
import axios from 'axios';
import Cookies from "universal-cookie"; 
import { Project, ProjectFetched, Skill } from './interfaces';
import Sidebar from './sidebar';
import Navbar from './navbar';


function App() {
  const [projects, setProjects] = useState<Project[]>()
  const [skills, setSkills] = useState<Skill[]>()
  const [name, setName] = useState<string>('')
  const [body, setBody] = useState<string>('')
  const [email, setEmail] = useState<string>('')
  const [success, setSuccess] = useState<string | null>(null)
  const [hoveredProject, setHoveredProject] = useState<number | null>(null);
  const [showToast, setShowToast] = useState(false);
  const [isMainVisible, setIsMainVisible] = useState(true);
  const [screenSize, setScreenSize] = useState(window.innerWidth);


  
  const production = true
  const imageRoot =  production ? '/static/images/' : './images/'
  const baseUrl = production ? window.location.origin : 'http://127.0.0.1:8000';

  const cookies = new Cookies()


  const axiosInstance = axios.create({
    headers: {
        'X-CSRFToken': cookies.get("csrftoken")
    }
  });


//fetching projects and skills from backend
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
    console.log(projects)
  }

  if (!skills?.[1]) {
    getSkills()
  }
}, [projects, skills, axiosInstance, baseUrl])


useEffect(() => {
  const sections = document.querySelectorAll('.container');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');  
      } else {
        entry.target.classList.remove('visible');  
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
    observer.disconnect();
  };
}, []);



//sending email 
  const sendEmail = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
     setSuccess('sending...')
    try {
      await axiosInstance.post(`${baseUrl}/api/send-confirmation/`, 
        {
          name,
          email,
          body
        }
      );
      setSuccess(null)
      setShowToast(true); 
      setName('')
      setBody('')
      setEmail('')
    } catch (error) {
      console.error('Error sending message:', error);
      setSuccess(null)
    }  

  }

//manage load of elements on scroll


//update skill to display just 4 at a time

  const chunkSize = 4;
  const chunkedSkills = [];
  for (let i = 0; i < (skills? skills.length : 0); i += chunkSize) {
    chunkedSkills.push(skills?.slice(i, i + chunkSize));
  }

//display arrow when main section is not visible

  useEffect(() => {
    const mainSection = document.querySelector("#main");

    if (mainSection) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          setIsMainVisible(entry.isIntersecting);
        },
        {
          root: null,  
          threshold: 0.1,  
        }
      );

      observer.observe(mainSection);

      return () => {
        observer.disconnect();
      };
    }
  }, []);


//dinamic update of screen size variable
  useEffect(() => { 
    const handleResize = () => {
      setScreenSize(window.innerWidth,);
    };
 
    window.addEventListener("resize", handleResize);
 
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []); 

  
  
  return (
    <>
      {screenSize > 430 ? <Sidebar/>: <Navbar/>}

      
      <a href='#main' ><img className='arrow z-3' src={imageRoot + 'up-arrow.png'} style={{display: isMainVisible ? "none" : "block"}}/></a>
      <div className='sections-wrapper'>

        <section id="main" className=' d-flex' >
          <div className="container p-0  m-0 p-lg-5">
            <Row className="align-items-center text-sm-center">
              <Col xs={12} md={6} lg={7} className='text-center pl-5' >
                  <Row >
                    <h1 className=" m-0 p-0 fw-bold">Anastasiia Skachenko</h1>
                  </Row>
                  <Row > 
                    <h3 className="p-0">Front-end Developer</h3>
                  </Row>
                  <Row className='justify-content-center'>
                  <img src={`${imageRoot}/cat-typing.gif`} style={{width: "5em"}}/>
                  </Row>

              </Col>
              <Col xs={12} md={6} lg={5} className="d-flex justify-content-center  pl-5 pl-md-2 ">
                <Row className='justify-content-center'>
                  <div  className='photo d-flex align-content-center justify-content-center'> 
                      <img src={`${imageRoot}/me13.PNG`} alt="Profile" />
                  
                  </div>
                </Row>

              </Col>
            </Row>
            <Row className="align-items-center justify-content-center mt-0 mt-lg-3 p-0 p-lg-2 ">
              <Col xs={12} md={12} lg={6} className='p-0 p-lg-2'  >
                <div className="projects-container p-4">
                  <h4 className='text-white' >Projects</h4>
                    <div className=' row d-grid'>
                      <div className='slider slider-project'>
                        <div className='slide-track projects d-flex' style={{width: (projects?.length ?? 0) * 2 * 13 + 'em'}}>
                        {projects?.map((project, index) => (
                          <div key={project.name} 
                            className= 'slide-project d-flex align-items-center p-2' 
                            onMouseEnter={() => setHoveredProject(index)}
                            onMouseLeave={() => setHoveredProject(null)}>
                              <a href='#projects' className='text-decoration-none'> {hoveredProject === index ? "View More" : project.name}</a>
                            
                          </div>
                        ))}
                        {projects?.map((project, index) => (
                          <div key={project.name} 
                            className='slide-project d-flex align-items-center p-2' 
                            onMouseEnter={() => setHoveredProject(index)}
                            onMouseLeave={() => setHoveredProject(null)}>
                              <a href='#projects' className='text-decoration-none'> {hoveredProject === index ? "View More" : project.name}</a>
                            
                          </div>
                        ))}
                        </div>
                      </div>
                    </div>
                </div>
              </Col>
              <Col xs={12} md={12} lg={6}  className='d-flex justify-content-center'>
                <div className="skills-container p-4">

                  <h4 className='mb-0 mb-lg-4 text-white'>Skills</h4>
                  <div className="row d-grid">
                    <div className='slider position-relative d-grid '>
                      <div className='slide-track d-flex' style={{width: (skills?.length ?? 0) * 2 * 15 + 'em'}}>
                        {skills?.map(skill => (
                          <div key={skill.name} className='slide-skill d-flex align-items-center p-2'>
                            <img src={imageRoot + skill.image} className='skill-image' />
                          </div>
                        ))}
                        {skills?.map(skill => (
                          <div key={skill.name} className='slide-skill d-flex align-items-center p-2'>
                            <img src={imageRoot + skill.image} className='skill-image'/>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <a href='#skills' className='text-white text-decoration-none  '>See more</a>
                </div>

              </Col>
  
            </Row>
          </div>

        </section>

        <section id="about-me" className="d-flex align-items-center justify-content-center">
          <div className="container">
            <Row className="justify-content-center">
              <div className="col-12 col-md-6 col-lg-6  text-center justify-content-center ">
                <h1 className="mb-4">About Me</h1>
                <p className='text-center w-100' >
                  I am a Front-End Developer with 2 years of experience building
                  applications using vanilla JavaScript and React.js. I have developed
                  user-friendly and visually appealing applications for business such
                  as beauty salons and restaurants. While I specialize in front-end
                  development, I have a strong foundation in web technologies,
                  ensuring seamless integration of responsive designs with back-end
                  systems.
                </p>

              </div>
            </Row>
            <footer className="text-violet py-3 py-sm-4 py-md-2 mt-0 mt-lg-5 ">
      <div className=" text-center">
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
          <ul className="list-unstyled d-flex align-items-center justify-content-center mt-0 mt-sm-3 gap-2">
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
     </footer>

          </div>
        </section>

        <section id="projects" className='d-flex  align-items-center'>
          <div className="container">
            <div >
              <h1 className=" mb-4 text-center">Projects</h1>
              <div className='d-flex justify-content-center'>
                <div id="carouselProjects" className="carousel slide" data-bs-ride="carousel" data-bs-touch="true">
                  <div className="carousel-indicators ">
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


      <section id="contact" >
        <div className="container text-center align-items-center  ">
          <h1 className='mb-0 text-center' >Contact Me</h1>
          <p  >Feel free to get in touch with me for collaboration, feedback, or just a friendly chat!</p>
      
          <Row className="justify-content-center ">
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
                <ToastContainer position="top-end" className='mt-4'>
                  <Toast
                    show={showToast}
                    onClose={() => setShowToast(false)}
                    delay={3000} // Duration for auto-hide in milliseconds
                    autohide
                  >
                     
                    <Toast.Body>I got your message!</Toast.Body>
                  </Toast>
                </ToastContainer>
              </form>
            </div>
          </Row>
        </div>
        
      </section>
    </div>
  </>
  )
}

export default App
