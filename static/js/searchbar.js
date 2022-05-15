function shead() {
  var input, filter, ul, lih, a, i, txtValue;
  input = document.getElementById('headInput');
  filter = input.value.toUpperCase();
  ul = document.getElementById("headUL");
  lih = ul.getElementsByTagName('li');

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < lih.length; i++) {
    a = lih[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      lih[i].style.display = "";
    } else {
      lih[i].style.display = "none";
    }
  }
}

function sbody() {
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById('bodyInput');
  filter = input.value.toUpperCase();
  ul = document.getElementById("bodyUL");
  li = ul.getElementsByTagName('li');

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}

function setHeadText(value) {
	document.getElementById("headInput").value = value;
}

function setBodyText(value) {
  document.getElementById("bodyInput").value = value;
}

function swapHeadBody() {
	headValue = document.getElementById("headInput").value;
	bodyValue = document.getElementById("bodyInput").value;
	headInput = input = document.getElementById('headInput');
	bodyInput = input = document.getElementById('bodyInput');
	headInput.value = bodyValue;
	bodyInput.value = headValue;
}

function copyPokedexToClipboard() {
  var copyText = document.getElementById("pokedexInput");
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */
  console.log(copyText.value);
  navigator.clipboard.writeText(copyText.value);
} 