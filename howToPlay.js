const images = [
    "https://i.pinimg.com/736x/22/c7/2d/22c72d7c8ace364865779c54a8875b03.jpg",
    "https://i.pinimg.com/736x/de/fe/e5/defee51681cf6bdeb20deccf9345f368.jpg",
    "https://i.pinimg.com/736x/47/6d/5c/476d5c93c3df80c259ad038791d4e57b.jpg",
    "https://i.pinimg.com/736x/6f/ce/b0/6fceb098d032f50b4668957569d6446d.jpg",
    "https://i.pinimg.com/736x/0e/7a/9f/0e7a9fd185f853b6f3cd6d103d514514.jpg",
    "https://i.pinimg.com/736x/a9/2c/74/a92c7441cb7914193109dfc77905bd8e.jpg",
    "https://i.pinimg.com/736x/ba/0b/6e/ba0b6e51f7757c09ccd0905e511ebc1c.jpg"
  ];
 
const slideshowImage = document.getElementById('slideshow-image');


let currentIndex = 0;


function showNextImage() {
  currentIndex = (currentIndex + 1) % images.length; 
  slideshowImage.style.opacity = 0; 
  setTimeout(() => {
    slideshowImage.src = images[currentIndex]; 
    slideshowImage.style.opacity = 1; 
  }, 500); 
}


slideshowImage.addEventListener('click', showNextImage);