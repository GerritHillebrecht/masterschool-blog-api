// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            build_posts(data)
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    const baseUrl = document.getElementById('api-base-url').value;
    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;
    const author = document.getElementById('post-author').value ?? "John Doe";
    const categories = document.getElementById('post-categories').value?.split(",").map(category => category.trim()) ?? [];
    const tags = document.getElementById('post-tags').value.split(",").map(category => category.trim()) ?? [];


    if (!title || !content || !author || !categories || !tags) {
        return alert("Missing input")
    }

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title,
            content,
            author,
            categories,
            tags
        })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

function addComment(post_id) {
    const baseUrl = document.getElementById('api-base-url').value;
    const title = document.getElementById(`title-${post_id}`).value
    const comment = document.getElementById(`comment-${post_id}`).value
    const author = document.getElementById(`author-${post_id}`).value

    if (!title || !comment || !author) {
        return alert("Please fill in all required fields.")
    }

    fetch(baseUrl + '/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            post_id,
            title,
            author,
            comment
        })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(comment => {
        console.log('Comment added:', comment);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

function deleteComment(commentId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/comments/' + commentId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Comment deleted:', commentId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

function veryShittySearch() {
    const baseUrl = document.getElementById('api-base-url').value;
    const search_str = document.getElementById("search_bar").value;

    if (!search_str) {
        return alert("Please enter a search string.")
    }

    const asd = {
        "title": document.getElementById("checked_title").checked,
        "content": document.getElementById("checked_content").checked
    };

    hasSelection = Object.values(asd).some(value => value)

    if (!hasSelection) {
        return alert("Please decide WHERE you want to search.")
    }

    search_string = Object.keys(asd).filter(key => asd[key]).map(key => `${key}=${search_str}`).join("&")
    searchURI = `${baseUrl}/posts/search?${search_string}`

    fetch(searchURI)
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            build_posts(data)
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console

}

function build_posts(data) {
    const postContainer = document.getElementById('post-container');
    postContainer.innerHTML = '';

    // For each post in the response, create a new post element and add it to the page
    data.forEach((post, index) => {
        tags = post.tags.map(tag => `<span class="badge rounded-pill text-bg-secondary">${tag}</span>`).join("")
        const postDiv = document.createElement('div');
        postDiv.className = 'post card';
        postDiv.innerHTML = `
            <div class="card-body">
                <h2 class="card-title">${post.title}</h2>
                <div class="d-flex align-items-center gap-1">
                    ${tags}
                </div>
                <hr />
                <p class="card-text">${post.content}</p>
                <button class="btn-delete" onclick="deletePost(${post.id})">Delete</button>
                <hr />

                <p class="">Comments</p>
                <div class="input-field-group">
                    <div class="input-field">
                        <input id="author-${post.id}" type="text" placeholder="Your name" />
                    </div>
                    <div class="input-field">
                        <input id="title-${post.id}" type="text" placeholder="Title of your comment" />
                    </div>
                </div>
                <textarea id="comment-${post.id}" placeholder="Add a new comment" rows="3"></textarea>
                <button class="btn btn-primary" onclick="addComment(${post.id})">Add Comment</button>
            </div>
        `;
        const commentBoxDiv = document.createElement("div");
        commentBoxDiv.className = "comment-box p-3";
        post.comments?.forEach(comment => {
            const commentDiv = document.createElement("div");
            commentDiv.className = "card";
            commentDiv.innerHTML = `
                <div class="card-body">
                    <span class="badge rounded-pill text-bg-primary">${comment.author}</span>
                    <h5 class="card-title">${comment.title}</h5>
                    <p class="card-text">${comment.comment}</p>
                    <button class="btn-delete" onclick="deleteComment(${comment.id})">Delete</button>
                </div>
            `;
            commentBoxDiv.appendChild(commentDiv)
        })
        postDiv.appendChild(commentBoxDiv)
        postContainer.appendChild(postDiv);
    });
}