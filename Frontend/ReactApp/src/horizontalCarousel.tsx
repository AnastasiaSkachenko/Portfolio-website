import React, { useRef, useEffect } from "react";

interface Skill {
  name: string;
  image: string;
  experience: number;
}

interface HorizontalCarouselProps {
  skills: Skill[];
  imageRoot: string;
}

const HorizontalCarousel: React.FC<HorizontalCarouselProps> = ({ skills, imageRoot }) => {
  const carouselRef = useRef<HTMLDivElement>(null);
  let startX: number = 0;

  useEffect(() => {
    const carousel = carouselRef.current;

    const handleTouchStart = (event: TouchEvent) => {
      startX = event.touches[0].clientX; // Record the starting X position
    };

    const handleTouchMove = (event: TouchEvent) => {
      if (!startX) return;

      const endX = event.touches[0].clientX; // Record the ending X position
      const diff = startX - endX;

      // Threshold for swipe gesture
      if (Math.abs(diff) > 50) {
        if (diff > 0) {
          // Swipe left -> Next slide
          carousel?.querySelector<HTMLButtonElement>(".carousel-control-next")?.click();
        } else {
          // Swipe right -> Previous slide
          carousel?.querySelector<HTMLButtonElement>(".carousel-control-prev")?.click();
        }
        startX = 0; // Reset starting X position
      }
    };

    if (carousel) {
      carousel.addEventListener("touchstart", handleTouchStart);
      carousel.addEventListener("touchmove", handleTouchMove);
    }

    return () => {
      if (carousel) {
        carousel.removeEventListener("touchstart", handleTouchStart);
        carousel.removeEventListener("touchmove", handleTouchMove);
      }
    };
  }, []);

  return (
    <div
      id="horizontalCarousel"
      className="carousel slide"
      ref={carouselRef}
    >
      {/* Dots for slide indicators */}
      <div className="carousel-indicators">
        {skills.map((_, index) => (
          <button
            key={index}
            type="button"
            data-bs-target="#horizontalCarousel"
            data-bs-slide-to={index}
            className={index === 0 ? "active" : ""}
            aria-current={index === 0 ? "true" : "false"}
            aria-label={`Slide ${index + 1}`}
          ></button>
        ))}
      </div>

      {/* Carousel Items */}
      <div className="carousel-inner">
        {skills.map((skill, index) => (
          <div
            key={skill.name}
            className={`carousel-item ${index === 0 ? "active" : ""}`}
          >
            <div className="card text-center shadow border-light rounded-3">
              <img
                src={imageRoot + skill.image}
                alt={skill.name}
                className="card-img-top"
                style={{ height: "35px", objectFit: "contain" }}
              />
              <div className="card-body">
                <p className="card-title fw-bold">{skill.name}</p>
                <p className="card-text text-muted">
                  {skill.experience} {skill.experience > 1 ? "years" : "year"} of
                  experience
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Navigation Buttons */}
      <button
        className="carousel-control-prev"
        type="button"
        data-bs-target="#horizontalCarousel"
        data-bs-slide="prev"
      >
        <span className="carousel-control-prev-icon" aria-hidden="true"></span>
        <span className="visually-hidden">Previous</span>
      </button>
      <button
        className="carousel-control-next"
        type="button"
        data-bs-target="#horizontalCarousel"
        data-bs-slide="next"
      >
        <span className="carousel-control-next-icon" aria-hidden="true"></span>
        <span className="visually-hidden">Next</span>
      </button>
    </div>
  );
};

export default HorizontalCarousel;
