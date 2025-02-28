$(document).ready(function () {
    $('#logout').click(function () {
        $.ajax({
            url: '/logout',
            type: 'GET',
            success: function (response) {
                window.location.href = '/login';
            },
            error: function (xhr, status, error) {
                console.error('Logout failed:', error);
            }
        });
    });
});

$.ajaxSetup({async: false});

let listOfItems = []
$.ajax({
    url: '/api/products?group_id=' + localStorage.getItem('group_id'),
    method: 'get',
    dataType: 'json',
    success: function (data) {
        listOfItems = data
    }
});

const shop_window = document.querySelector(".main_section")
for (let element of listOfItems) {
    let card = document.createElement('div');
    card.classList.add('card');
    shop_window.appendChild(card);
    let img = document.createElement('img');
    img.src = element.url;
    img.alt = element.name;
    card.appendChild(img);
    let h3 = document.createElement('h3')
    h3.textContent = element.name;
    card.appendChild(h3);
    card.addEventListener('click', function () {
        window.location.href = "/product/" + element.id;
    });
}

