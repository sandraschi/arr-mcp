let _permissionGranted = false;

export function requestNotificationPermission(): boolean {
	if (!("Notification" in window)) return false;
	if (Notification.permission === "granted") {
		_permissionGranted = true;
		return true;
	}
	if (Notification.permission === "default") {
		Notification.requestPermission().then((p) => {
			_permissionGranted = p === "granted";
		});
	}
	return false;
}

export function sendNotification(title: string, options?: NotificationOptions) {
	if (!("Notification" in window)) return;
	if (Notification.permission === "granted") {
		new Notification(title, options);
	}
}
