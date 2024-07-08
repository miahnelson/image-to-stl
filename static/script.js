document.getElementById('file').addEventListener('change', function(event) {
    var file = event.target.files[0];
    var reader = new FileReader();
    reader.onload = function(e) {
        var img = document.getElementById('image-preview');
        img.src = e.target.result;
        img.style.display = 'block';
    };
    reader.readAsDataURL(file);
});

document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);

    // Show the processing animation
    document.getElementById('processing-animation').style.display = 'block';

    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('processing-animation').style.display = 'none';  // Hide the processing animation
        if (data.success) {
            var downloadLink = document.getElementById('download-link');
            downloadLink.href = data.stl_url;
            downloadLink.style.display = 'block';

            var viewStlButton = document.getElementById('view-stl-button');
            viewStlButton.setAttribute('data-url', data.stl_url);
            viewStlButton.style.display = 'block';
        } else {
            console.error(data.error);
        }
    })
    .catch(error => {
        document.getElementById('processing-animation').style.display = 'none';  // Hide the processing animation
        console.error('Error:', error);
    });
});

function updateOutputWidthLabel() {
    const outputWidth = parseInt(document.getElementById('output_width').value, 10);
    const widthInMM = (outputWidth / 96) * 25.4;
    document.getElementById('output_width_label').textContent = `Output Width in pixels (default: ${outputWidth}) - ${widthInMM.toFixed(2)} mm`;
}

function viewStl() {
    var button = document.getElementById('view-stl-button');
    var stlUrl = button.getAttribute('data-url');
    var viewerUrl = window.location.origin + "/viewer?file=" + encodeURIComponent(stlUrl);
    window.open(viewerUrl, "STL Viewer", "width=800,height=600");
}
