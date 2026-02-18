const foodData = [
    { name: 'Makanan Indonesia' },
    { name: 'Nasi Goreng' },
    // Add more food items as needed
];

function displayFoodList() {
    const foodListElement = document.getElementById('food-list');
    foodData.forEach(food => {
        const liElement = document.createElement('li');
        liElement.textContent = food.name;
        foodListElement.appendChild(liElement);
    });
}
displayFoodList();