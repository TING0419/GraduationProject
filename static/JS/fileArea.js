const dragArea = document.querySelector('.drag-area');
const dragText = document.querySelector('.header');

let input = document.querySelector('input[type="file"]');

let file;

input.addEventListener('change', function(){
    file = this.files[0];
    dragArea.classList.add('active');
    displayFile();
})

// when file is inside the drag area
dragArea.addEventListener('dragover', (event) => {
    event.preventDefault();
    dragArea.classList.add('active');
});

// when file leaves the drag area
dragArea.addEventListener('dragleave', (event) => {
    dragArea.classList.remove('active');
});

// when file is dropped in the drag area
dragArea.addEventListener('drop', (event) => {
    event.preventDefault();
    file = event.dataTransfer.files[0];
    displayFile();
});

function displayFile(){
    let fileType = file.type;
    let validExtensions = ['image/jpg', 'image/png', 'image/jpeg'];
    if(validExtensions.includes(fileType)){
        let fileReader = new FileReader();

        fileReader.onload = () =>{
            let fileURL = fileReader.result;
            let imgTag = `<img src="${fileURL}" alt="">`;
            dragArea.innerHTML = imgTag;
        };
        fileReader.readAsDataURL(file)
    }
    else
    {
        alert('This file is not an Image')
        dragArea.classList.remove('active');
    }
}