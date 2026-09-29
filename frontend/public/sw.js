self.addEventListener("push",event=>{
 const d=event.data?event.data.json():{title:"NotifyHub",body:"New notification"};
 event.waitUntil(self.registration.showNotification(d.title,{body:d.body,icon:"/icon.svg"}));
});
self.addEventListener("notificationclick",event=>{
 event.notification.close(); event.waitUntil(clients.openWindow("/"));
});
