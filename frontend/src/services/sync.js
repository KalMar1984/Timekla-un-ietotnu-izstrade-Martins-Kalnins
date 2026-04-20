import axios from 'axios';
import { db } from '../db';

const BASE_URL = 'http://127.0.0.1:5000/api';

export const syncData = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        // 1. DOWNLOAD PHASE: Get entries from backend
        console.log('Sync service: Fetching entries from backend...');
        const response = await axios.get(`${BASE_URL}/entries`, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 5000
        });
        
        const remoteEntries = response.data;
        let syncedCount = 0;
        for (const remoteEntry of remoteEntries) {
            // Strip the remote ID to avoid conflicting with Dexie's auto-incrementing ID
            const { id, ...entryData } = remoteEntry;
            
            // Find if we have it locally by date
            const localEntry = await db.entries.where('date').equals(remoteEntry.date).first();
            
            if (localEntry) {
                // Update local if it's already synced (remote is source of truth for historical)
                if (localEntry.sync_status !== 'pending') {
                    await db.entries.update(localEntry.id, {
                        ...entryData,
                        sync_status: 'synced'
                    });
                    syncedCount++;
                }
            } else {
                // Add new local entry
                await db.entries.add({
                    ...entryData,
                    sync_status: 'synced'
                });
                syncedCount++;
            }
        }
        if (syncedCount > 0) {
            console.log(`Sync service: Successfully downloaded/updated ${syncedCount} entries.`);
        }

        // 2. UPLOAD PHASE: Find unsynced entries
        const pendingEntries = await db.entries.where('sync_status').equals('pending').toArray();
        if (pendingEntries.length > 0) {
            console.log(`Sync service: Found ${pendingEntries.length} pending entries. Starting upload...`);
        }
        
        for (const entry of pendingEntries) {
            try {
                await axios.post(`${BASE_URL}/entries`, entry, {
                    headers: { Authorization: `Bearer ${token}` },
                    timeout: 5000
                });
                
                // Update local status to synced
                await db.entries.update(entry.id, { sync_status: 'synced' });
                console.log(`Sync service: Successfully synced entry for ${entry.date}`);
            } catch (err) {
                console.error(`Sync service: Failed to sync entry for ${entry.date}:`, err.message);
            }
        }
    } catch (err) {
        console.error('Sync service error:', err);
    }
};

// Initial sync call
syncData();

// Check network status and sync
window.addEventListener('online', syncData);
setInterval(syncData, 60000); // Try every minute
