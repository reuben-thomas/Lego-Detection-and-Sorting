eel.setup()

eel.expose(updateImageSrc)
function updateImageSrc(val, id) {
  let elem = document.getElementById(id);
  if (val == "") 
  {
    elem.src = "";
  }
  else
  {
    elem.src = "data:image/jpeg;base64," + val;
  }
}

eel.expose(updateListSrc)
function updateListSrc(commaSeparatedValues, idsToSend) {
  const values = commaSeparatedValues.split(',')
  const ids = idsToSend.split(',')
  values.forEach((value, idx)=>{
    document.getElementById(ids[idx]).innerHTML = value;
  })
}

eel.expose(updateTextSrc)
function updateTextSrc(val,id) {
  document.getElementById(id).innerHTML = val;
}
eel.expose(updateImageSrc)
function updateImageSrc(val, id) {
  let elem = document.getElementById(id);
  elem.src = "data:image/jpeg;base64," + val;
}

function py_video() {
   eel.video_feed()()
}

let captureActive = true;

eel.expose(get_Option)
function get_Option() {
  selectedOption = $('#idOption').val()
  return selectedOption;
}

eel.expose(get_Value)
function get_Value(id) {
  selectedVal= document.getElementById(id).innerHTML
  return selectedVal;
}

$(function(){

  $(".dropdown-menu a").click(function(){

    $('#selected_video').text($(this).text());
    $('#selected_video').val($(this).text());

 });
});

$(document).ready(function() {
  
  // Get click event, assign button to var, and get values from that var
  $('#disp_mode button').on('click', function() {
    var thisBtn = $(this);    
    thisBtn.addClass('active').siblings().removeClass('active');
    var btnText = thisBtn.text();
    console.log(btnText + ' - ' + btnValue);
  });
  
  // You can use this to set default value
  // It will fire above click event which will do the updates for you
  $('#disp_mode button[text="Detection"]').click();
});

eel.expose(get_Output)
function get_Option(output) {
  selectedOption = $('#disp_mode').text()
  return selectedOption;
}

$(document).ready(function(){
  $('[data-toggle="popover"]').popover();
});
