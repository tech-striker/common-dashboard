/* globals io */


function chatHTML(message, user, timestamp) {
    return `
    <div class="row my-0" id="message-format">
      <div class="col-6">
        <p class="text-left font-weight-light my-0" id="message-timestamp">${timestamp}</p>
      </div>
      <div class="col-6">
        <p class="text-right font-weight-bold my-0" id="message-username">${user}</p>
      </div>
      <div class="col-12">
        <p class="text-right my-0" id="message-text">${message}</p>
      </div>
    </div>`;
}

function select_chat(room_id) {
    localStorage.setItem('currentRoom', room_id)
    fetch(`${window.location.protocol}//${document.domain}:${window.location.port}/api/message/?room=${room_id}`, headers = {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    })
        .then(response => response.json())
        .then(data => {
            debugger
            const messages = data.data.messages;
            currentRoom = data.data.room;
            // Save the current channel into the local storage
            localStorage.setItem('currentRoom', currentRoom);

            // Highlight the chatroom button that the user is currently in
            document.getElementById(currentRoom).className = 'btn btn-primary';

            // Define the chatroom div
            const chatroom = document.querySelector('#messages-list');

            // Delete the messages for the previous chatroom by removing first child
            while (chatroom.firstChild) {
                chatroom.removeChild(chatroom.firstChild);
            }

            // Load the messages for the chatroom
            messages.forEach(messageItem => {
                // Create the divider element
                const divider = document.createElement('hr');
                divider.className = 'my-1';

                // Append the divider element
                chatroom.appendChild(divider);

                // Extract the timestamp, username, and message
                const {message_body} = messageItem;
                const timestamp = messageItem.created_at;
                const user = messageItem.sender.email;

                // Create chat message div
                const div = document.createElement('div');
                div.innerHTML = chatHTML(message_body, user, timestamp); // returns custom HTML string
                chatroom.appendChild(div);

                // Move the scrollbar to the bottom of the chat
                const objDiv = document.getElementById('messages-list');
                objDiv.scrollTop = objDiv.scrollHeight;
            });


        })
        .catch((error) => {
            console.error('Error:', error);
        });


}


document.addEventListener('DOMContentLoaded', () => {
    // Global vars
    let username = null;
    let currentRoom = null;

    // Hide the chatroom initially
    const form = document.querySelector('#chatroom');
    form.style.display = 'none';

    // Connect to websocket
    const socket = io.connect(`${window.location.protocol}//${document.domain}:${window.location.port}`, (socket) => {
        console.log('dfadfsafs', socket.id)
    });
    socket.emit('get_chats', {'token': localStorage.getItem('token')}, (callback) => {
        console.log(callback)
    })

    // By default, ensure the login submit button is disabled
    document.querySelector('#login_submit_button').disabled = true;

    // By default, ensure the channel button is disabled
    document.querySelector('#new-channel-button').disabled = true;

    // Enable user submit button only if there is text in the input field
    document.querySelector('#username-input').onkeyup = () => {
        if (document.querySelector('#username-input').value.length > 0)
            document.querySelector('#login_submit_button').disabled = false;
        else document.querySelector('#login_submit_button').disabled = true;
    };

    // Enable new channel button only if there is text in the input field
    document.querySelector('#new-channel-input').onkeyup = () => {
        if (document.querySelector('#new-channel-input').value.length > 0)
            document.querySelector('#new-channel-button').disabled = false;
        else document.querySelector('#new-channel-button').disabled = true;
    };

    // Define the unhide chatroom function
    function unhideChatroom() {
        // Unhide the chatroom
        const chatroom = document.querySelector('#chatroom');
        chatroom.style.display = 'block';

        // Hide the user submission form
        const div = document.querySelector('#user-submission-div');
        div.style.display = 'none';

        // Show the username in index.html
        document.querySelector('#hello-user').innerHTML = username;
    }

    function configureButton(button) {
        // When a channel button is clicked
        button.onclick = () => {
            console.log('dfjslkj')
            // Check that the user is NOT in the channel chatroom yet
            if (currentRoom !== button.id) {
                // Unhighlight the current channel button
                if (currentRoom !== null) {
                    document.getElementById(currentRoom).className =
                        'btn btn-secondary';
                }
                // Emit to the serve that the user is moving to the channel
                socket.emit('move to channel', {
                    channel: button.id,
                });
            }

            // Stop button from refreshing
            return false;
        };
    }


    // When connected, configure submission forms and buttons
    socket.on('connect', () => {
        // ? When the username is submitted
        socket.emit('connected', {token: localStorage.getItem('token'), 'sid': socket.io.engine.id});
        document.querySelector('#new-user-form').onsubmit = () => {
            // Grab the username from the input field
            const usernameTemp = document.querySelector('#username-input').value;
            return false;
        };

        // ? If the username is already set in local storage
        if (localStorage.getItem('token')) {
            // Unhide chatroom
            unhideChatroom();

            // Verify the local storage channel name first
            socket.emit('verify channel', {channel: currentRoom});

            // Store username and current channel
            username = localStorage.getItem('username');
            currentRoom = localStorage.getItem('currentRoom');

            // Show the username in index.html
            document.querySelector('#hello-user').innerHTML = username;

            // Check with the server that this 'username' is accounted for
            socket.emit('confirm login', {username});

            // Move the user to the saved channel
            socket.emit('move to channel', {channel: currentRoom});
        }

        // ? Configure the Create channel form
        document.querySelector('#new-channel-form').onsubmit = () => {
            console.log('dfasldkfjdlskjl')
            // Add the channel name to the local vars in this function
            const channel = document.querySelector('#new-channel-input').value;

            // Clear the input field and disable the button again
            document.querySelector('#new-channel-input').value = '';
            document.querySelector('#new-channel-button').disabled = true;
            data = {
                name: channel,
                participants: ['61010d7ce4c9786a417b4113'],
                Authorization: localStorage.getItem('token'),
                is_group: true
            }

            // Broadcast the channel creation to the server
            socket.emit('new_room_create', data);

            // Stop form from refreshing
            return false;
        };

        // ? Configure the channel list buttons
        document.getElementsByName('channel-button').forEach(button => {
            configureButton(button);
        });

        // ? Configure the send message form
        document.querySelector('#submit-message-form').onsubmit = () => {
            // Grab the message
            const message = document.querySelector('#submit-message-input').value;

            // Clear the input field
            document.querySelector('#submit-message-input').value = '';
            // Broadcast the message AND channel to the server
            socket.emit('new_message', {
                room: localStorage.getItem('currentRoom'),
                message_body: message,
                type: 'USER_TEXT_MESSAGE',
                token: localStorage.getItem('token'),
            });

            // Prevent the submission from refreshing
            return false;
        };
    });

// ? If channel name fails, throw up an alert
    socket.on('room_creation_failed', () => {
        alert('Channel already exists. Try another name.');
    });

    socket.on('set_chats', data => {
        html = ''
        for (let d of data['chats']) {
            id = d['id']
            html += `<button class="btn btn-secondary" id="${d['id']}" name="channel-button" onclick="select_chat(id)" type="submit">${d['name']}</button>`
        }
        document.getElementById('channel-button-list').innerHTML = html
    })

// ? If channel name was successful
    socket.on('add_room', data => {
        // Grab the channel name added, uses object destructuring
        const {channel} = data;
        // Create the button for the channel
        console.log('dfaljdlkfsaklfjlksfkl;jsdl')
        const button = document.createElement('button');
        button.className = 'btn btn-secondary';
        button.id = channel.name;
        button.innerHTML = channel.name;

        // Configure the button clicking features
        configureButton(button);

        // Add the button to the channel list
        document.querySelector('#channel-button-list').append(button);
    });

// ? If the username logs in successfully
//     socket.on('new user', data => {
//         // Update the global username
//         // eslint-disable-next-line prefer-destructuring
//         username = data.username;
//         // Add the username and current channel to the local storage
//         localStorage.setItem('username', username);
//         localStorage.setItem('currentRoom', 'Main Channel');
//
//         // Remove the 'username taken' prompt if it is there
//         let paragraph = document.querySelector('#username-taken').innerHTML;
//         if (paragraph !== '') {
//             paragraph = '';
//         }
//
//         // Unhide the chatroom
//         unhideChatroom();
//
//         // Show the username in index.html
//         document.querySelector('#hello-user').innerHTML = data.username;
//
//         // Move the user to the default channel
//         // Emit to the serve that the user is moving to the channel
//         socket.emit('move to channel', {channel: 'Main Channel'});
//     });

// ? If the username is already taken
    socket.on('username taken', () => {
        // Alert the user that the name is taken
        document.querySelector('#username-taken').innerHTML =
            '<i class="my-0">Username taken!</i>';
    });


// ? Enters the channel room, unload previous chat, load new chat
//     socket.on('enter_channel_room', data => {
//         // Set variables
//         const {messages} = data;
//         currentRoom = data.channel;
//         // Save the current channel into the local storage
//         localStorage.setItem('currentRoom', currentRoom);
//
//         // Highlight the chatroom button that the user is currently in
//         document.getElementById(currentRoom).className = 'btn btn-primary';
//
//         // Define the chatroom div
//         const chatroom = document.querySelector('#messages-list');
//
//         // Delete the messages for the previous chatroom by removing first child
//         while (chatroom.firstChild) {
//             chatroom.removeChild(chatroom.firstChild);
//         }
//
//         // Load the messages for the chatroom
//         messages.forEach(messageItem => {
//             // Create the divider element
//             const divider = document.createElement('hr');
//             divider.className = 'my-1';
//
//             // Append the divider element
//             chatroom.appendChild(divider);
//
//             // Extract the timestamp, username, and message
//             const {message} = messageItem;
//             const {timestamp} = messageItem;
//             const user = messageItem.username;
//
//             // Create chat message div
//             const div = document.createElement('div');
//             div.innerHTML = chatHTML(message, user, timestamp); // returns custom HTML string
//             chatroom.appendChild(div);
//
//             // Move the scrollbar to the bottom of the chat
//             const objDiv = document.getElementById('messages-list');
//             objDiv.scrollTop = objDiv.scrollHeight;
//         });
//     });

    socket.on('message_broadcast', data => {
        // Set variable
        debugger;
        const {message_body} = data.message_body;
        const {room} = data;
        const {timestamp} = data;
        const user = data.sender.email;
        const chatroom = document.querySelector('#messages-list');

        // Check if the user is in the channel (whether they should see the message)
        if (currentRoom === room) {
            // Create the divider element
            const divider = document.createElement('hr');
            divider.className = 'my-1';

            // Append the divider element
            chatroom.appendChild(divider);

            // Create chat message div
            const div = document.createElement('div');
            div.innerHTML = chatHTML(message_body, user, timestamp); // returns custom-made string
            chatroom.appendChild(div);

            // Move the scrollbar to the bottom of the chat
            const objDiv = document.getElementById('messages-list');
            objDiv.scrollTop = objDiv.scrollHeight;
        }
    });

// ? Handle invalid channel name with a prompt
    socket.on('invalid channel name', () => {
        alert('Invalid channel name!');
    });

// ? Default channel name
    socket.on('default channel', () => {
        currentRoom = 'Main Channel';
    });
});
