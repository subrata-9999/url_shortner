function getDeviceId() {
    let id = localStorage.getItem("device_id");

    if (!id) {
        id = "dev-" + Math.random().toString(36).substring(2) + Date.now();
        localStorage.setItem("device_id", id);

        // Set cookie so backend receives it
        document.cookie = "device_id=" + id + "; path=/; max-age=31536000";

        // RELOAD PAGE ONE TIME
        location.reload();
        return;
    }

    // Ensure cookie exists for future GET
    document.cookie = "device_id=" + id + "; path=/; max-age=31536000";

    return id;
}

getDeviceId();
