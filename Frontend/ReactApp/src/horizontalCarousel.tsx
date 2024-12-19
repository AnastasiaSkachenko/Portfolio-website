import   { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Carousel } from 'react-bootstrap';
import { Skill } from './interfaces';

export interface Props {
  skills: Skill[],
  imageRoot: string
}

const ImageCarousel:React.FC<Props> = ({skills, imageRoot}) => {
  const [imagesPerSlide, setImagesPerSlide] = useState(1);

  const updateImagesPerSlide = () => {
    const width = window.innerWidth;

    if (width >= 1200) {
      setImagesPerSlide(4); // Show 4 images on large screens
    } else if (width >= 768) {
      setImagesPerSlide(3); // Show 3 images on medium screens
    } else if (width >= 576) {
      setImagesPerSlide(2); // Show 2 images on smaller screens
    } else {
      setImagesPerSlide(1); // Show 1 image on very small screens
    }
  };

  useEffect(() => {
    updateImagesPerSlide();
    window.addEventListener('resize', updateImagesPerSlide);

    return () => {
      window.removeEventListener('resize', updateImagesPerSlide);
    };
  }, []);

  // Chunk the images into groups based on screen size
  const chunkedImages = [];
  for (let i = 0; i < skills.length; i += imagesPerSlide) {
    chunkedImages.push(skills.slice(i, i + imagesPerSlide));
  }

  return (
    <Carousel className='imageCarousel'
      interval={1000} // Auto-rotate every 2 seconds
      controls={false} // No controls (next/prev buttons)
      indicators={false} // No indicators (dots)
      touch={true} // Allow swipe for touch devices
      wrap={true} // Loop the carousel infinitely
    >
      {chunkedImages.map((chunk, index) => (
        <Carousel.Item key={index}>
          <div className="d-flex">
            {chunk.map((skill, idx) => (
              <div key={idx} className="col-4 p-1">
                <img
                  className="skill-image"
                  src={imageRoot + skill.image}
                  alt={`Slide ${index * imagesPerSlide + idx + 1}`}
                  style={{ objectFit: 'cover' }}
                />
              </div>
            ))}
          </div>
        </Carousel.Item>
      ))}
    </Carousel>
  );
};

export default ImageCarousel;
