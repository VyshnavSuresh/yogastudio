//For Page Reloading
window.addEventListener( "pageshow", function ( event ) {
  var historyTraversal = event.persisted ||
                         ( typeof window.performance != "undefined" &&
                              window.performance.navigation.type === 2 );
  if ( historyTraversal ) {

    window.location.reload();
  }
});



const video = document.getElementById('video-player');
const progressBar = document.getElementById('progress_bar');

//For progress bar
video.addEventListener('timeupdate', () => {
  const progress = video.currentTime / video.duration;

  const current_progress=document.getElementById('value').innerHTML;
  progressBar.style.width = `${current_progress * 100}%`;
  if(parseInt(progress*100)>current_progress){
    progressBar.style.width = `${progress * 100}%`;
    document.getElementById('value').innerHTML=parseInt(progress*100);
  }
  else{
    progressBar.style.width = `${current_progress}%`;
  }
});

//For Progress_saving

video.addEventListener("pause", (event) => {
  const progress =parseInt(video.currentTime / video.duration*100);
  const current_progress=document.getElementById('value').innerHTML;
  var course=document.getElementById("video_title").innerHTML;

  if(parseInt(progress*100)>current_progress){


    $.ajax({
      url:"/progress/"+progress+"/"+course,
      context: progress
    })
  }

});
