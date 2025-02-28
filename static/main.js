
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

$.ajax({
    url: '/api/products?group_id=' + localStorage.getItem('group_id'),
    method: 'get',
    dataType: 'json',
    success: function (data) {
        listOfItems = data
    }
});


const maxCardInLine = 10000


// цикл для прохождения по строкам 
// maxCardInLine - максимальное кол-во карточек в строке
const rowCount = Math.ceil(listOfItems.length / maxCardInLine)

for (let i = 0; i < rowCount; i = i + 1) {

    const shop_window = document.querySelector(".main_section")

    // and == && , or = ||
    for (let j = 0, index = i * maxCardInLine; j < maxCardInLine && index < listOfItems.length; j = j + 1, index = i * maxCardInLine + j) {
        // index - номер карточки, j - карточка в строке от 0 до maxCardInLine (5) , i - номер строки
        let el = listOfItems[index]

        let card = document.createElement('div');
        card.classList.add('card');
        shop_window.appendChild(card);

        let img = document.createElement('img');
        img.src = el.url;
        img.alt = "картинка";
        card.appendChild(img);

        let h3 = document.createElement('h3')
        h3.textContent = el.name;
        card.appendChild(h3);

        // go to "/product/" + el.id
        card.addEventListener('click', function () {
            window.location.href = "/product/" + el.id;
        });
    }

}
