export interface Skill {
  name: string;
  image: string;
  experience: number;
}
  
export interface HorizontalCarouselProps {
  skills: Skill[];
  imageRoot: string;
}
  

export interface Project {
  name: string,
  description: string,
  tools: string[]
}


export interface ProjectFetched {
  name: string,
  description: string,
  tools: string

}

