document.addEventListener('DOMContentLoaded', function () {
    // QRコード読み取りのためのスクリプト
    const qrScanner = new QrScanner(document.getElementById('qr-video'), result => handleQrResult(result));
    qrScanner.start();

    function handleQrResult(result) {
        fetch('/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: result })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            // Add the new video to the list
            const videoList = document.getElementById('video-list');
            const newVideo = document.createElement('li');
            newVideo.textContent = data.filename;
            videoList.appendChild(newVideo);
        })
        .catch(error => console.error('Error:', error));
    }

    // ドラッグ＆ドロップのためのスクリプト
    const dragArea = document.querySelector('.drag-area');
    const dragText = document.querySelector('.header');
    let files;

    dragArea.addEventListener('dragover', (event) => {
        event.preventDefault();
        dragText.textContent = 'Release to Upload File';
        dragArea.classList.add('active');
    });

    dragArea.addEventListener('dragleave', () => {
        dragText.textContent = 'Drag & Drop to Upload File';
        dragArea.classList.remove('active');
    });

    dragArea.addEventListener('drop', (event) => {
        event.preventDefault();
        files = event.dataTransfer.files;
        dragArea.classList.remove('active');
        showFiles(files);
    });

    function showFiles(files) {
        if (files.length === 0) return;

        const fileList = document.querySelector('.file-list');
        fileList.innerHTML = '';

        for (let file of files) {
            const listItem = document.createElement('li');
            listItem.textContent = file.name;
            fileList.appendChild(listItem);
        }
    }

    document.getElementById('upload-button').addEventListener('click', () => {
        if (!files || files.length === 0) return;

        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            // Add the new video to the list
            const videoList = document.getElementById('video-list');
            for (let file of files) {
                const newVideo = document.createElement('li');
                newVideo.textContent = file.name;
                videoList.appendChild(newVideo);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Add logic to handle posting to Twitter
    document.getElementById('post-to-twitter').addEventListener('click', () => {
        const selectedVideo = document.querySelector('input[name="video"]:checked').value;
        const commentText = document.getElementById('comment-text').value;

        fetch('/post_to_twitter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ video: selectedVideo, comment: commentText })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        })
        .catch(error => console.error('Error:', error));
    });
});
