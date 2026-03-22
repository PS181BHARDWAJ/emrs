/*################ Developed By: Sanjoy Pal ######################*/
function refreshCaptcha(sufVal) {
    sufVal = (sufVal == undefined) ? '' : sufVal;
    var img = document.images['captcha' + sufVal];
    if (img != undefined)
        img.src = img.src.substring(0, img.src.lastIndexOf("?")) + "?rand=" + Math.random() * 1000 + "&sval=" + sufVal;
}