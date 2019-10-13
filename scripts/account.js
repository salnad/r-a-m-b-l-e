window.onload=function(){
  let entryCards=document.querySelectorAll('.entryCard');
  console.log(entryCards);
  for(i=0;i!=entryCards.length;i++){
    entryCard=entryCards[i];
    entryCard.addEventListener('click', process(i));
    function process(i){
      console.log("hi"+i);
      // let strDate=document.getElementById("strDate"+(i+1)).textContent;
      // let strTime=document.getElementById("strTime"+(i+1)).textContent;
      // let year=strDate.substring(6), month=strDate.substring(0,2)
      // let day=strDate.substring(3,5), hr=strTime.substring(0,2), min=strTime.substring(3,5),sumSeconds=20;
      // console.log(year + " "+month+" "+day+" "+hr+" "+min);
      // window.location.href = "/journal?key="+year+" "+month+" "+sumSeconds;

    }
  }

  let statsLabel=document.getElementById('stats-label')
  let statsIcon=document.getElementById('stats-icon')
  statsIcon.addEventListener('hover',function(){
    statsLabel.style.visibility='visible';
    console.log("hieee")
  });
}
// "/journal?key=" + str(newJournal.year) +" "+ str(newJournal.month) + " " + str(newJournal.sumSeconds)
