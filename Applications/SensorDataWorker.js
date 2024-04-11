let db;
const dbName = 'sensorDatabase';
const storeName = 'sensorData';
const dbVersion = 1;

const request = indexedDB.open(dbName, dbVersion);

request.onupgradeneeded = function(event) {
    console.log('Upgrading or creating the database.');
    db = event.target.result;
    if (!db.objectStoreNames.contains(storeName)) {
        console.log(`Creating object store: ${storeName}`);
        db.createObjectStore(storeName, { autoIncrement: true });
    }
};

request.onerror = function(event) {
    console.error('IndexedDB error:', event.target.errorCode);
};

request.onsuccess = function(event) {
    console.log('Database opened successfully.');
    db = event.target.result;
};

self.onmessage = function(event) {
    const { type, data, action } = event.data;

    if (action) {
        switch (action) {
            case 'clearData':
                clearSensorData();
                break;
            case 'deleteDatabase':
                deleteDatabase();
                break;
            default:
                console.log('Unknown action:', action);
        }
    } else if (type) {
        switch (type) {
            case 'accelerometer':
            case 'gravity':
            case 'gyroscope':
            case 'orientation':
            case 'inclinometer':
                storeSensorData(type, data);
                break;
            default:
                console.log('Unknown sensor type:', type);
        }
    } else {
        console.log('Unknown message format:', event.data);
    }
};

function storeSensorData(type, data) {
    if (!db) {
        console.error('Database is not initialized');
        return;
    }

    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const entry = {
        type: type,
        data: data,
        timestamp: new Date().toISOString()
    };
    const request = store.add(entry);

    request.onsuccess = function() {
        console.log(`${type} data stored successfully`);
    };

    request.onerror = function(event) {
        console.error(`${type} data storage error:`, event.target.errorCode);
    };
}

function clearSensorData() {
    if (!db) {
        console.error('Database is not initialized');
        return;
    }

    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    store.clear().onsuccess = function() {
        console.log('Sensor data cleared');
    };
}

function deleteDatabase() {
    if (db) {
        db.close();
    }
    const deleteRequest = indexedDB.deleteDatabase(dbName);
    deleteRequest.onsuccess = function() {
        console.log('Database deleted successfully');
        db = null;
    };
    deleteRequest.onerror = function(e) {
        console.error('Error deleting database', e);
    };
}

function deleteAndRecreateDatabase() {
    const deleteRequest = indexedDB.deleteDatabase('sensorDatabase');

    deleteRequest.onsuccess = function() {
        console.log('Database deleted successfully.');
        recreateDatabase();
    };

    deleteRequest.onerror = function(event) {
        console.error('Database deletion failed:', event.target.errorCode);
    };
}

function recreateDatabase() {
    const request = indexedDB.open('sensorDatabase', 1);

    request.onupgradeneeded = function(event) {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('sensorData')) {
            db.createObjectStore('sensorData', { autoIncrement: true });
        }
    };

    request.onsuccess = function() {
        console.log('Database recreated successfully.');
    };

    request.onerror = function(event) {
        console.error('Database recreation failed:', event.target.errorCode);
    };
}
