function toggle_password() {

  const passwordInput = document.getElementById('password');
  const toggleIcon = document.getElementById('toggle_password');

  if (passwordInput.type === 'password') {

    passwordInput.type = 'text';
    toggleIcon.src = 'static/images/invisible.png';
    toggleIcon.alt = 'Hide Password';
    toggleIcon.title = 'Hide Password';

  } else {

    passwordInput.type = 'password';
    toggleIcon.src = 'static/images/visible.png';
    toggleIcon.alt = 'Show Password';
    toggleIcon.title = 'Show Password';

  }

}


function search_todo() {
    var input, filter, list;
    input = document.getElementById('search_todo_input');
    filter = input.value.toUpperCase();
    list = document.getElementsByClassName("todo_list");

    for (i = 0; i < list.length; i++) {
        if (list[i].innerHTML.toUpperCase().indexOf(filter) > -1) {
            list[i].style.display = "";
        }else {
            list[i].style.display = "none";
        }
    }
}