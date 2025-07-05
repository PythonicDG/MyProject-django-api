importScripts("https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js");

firebase.initializeApp({
    apiKey: "AIzaSyDUh9VroA9VybQuiBypXR5ba9w17XEWny4",
    authDomain: "drf-project-4e879.firebaseapp.com",
    projectId: "drf-project-4e879",
    storageBucket: "drf-project-4e879.appspot.app",
    messagingSenderId: "952725174712",
    appId: "1:952725174712:web:d463e75e8fab69697f374d",
    measurementId: "G-C0DSQCPQ9V"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
  const title = payload.notification.title;
  const options = {
    body: payload.notification.body
  };
  self.registration.showNotification(title, options);
});
