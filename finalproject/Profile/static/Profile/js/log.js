function show_hide_password(target){
  console.log("GO!")
	let input = document.getElementById('password-input');
	if (input.getAttribute('type') == 'password') {
    console.log("TEXT")
		target.classList.add('view');
		input.setAttribute('type', 'text');
	} else {
    console.log("PASS")
		target.classList.remove('view');
		input.setAttribute('type', 'password');
	}
	return false;
}