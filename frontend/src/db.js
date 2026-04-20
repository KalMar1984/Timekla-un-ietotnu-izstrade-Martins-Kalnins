import Dexie from 'dexie';

export const db = new Dexie('TrisLabasLietasDB');

// Update schema: Using date as primary key might be easier for a daily diary, 
// but ++id is safer for multi-entry. Let's stick to ++id but add index.
// Version 3: Force refresh and add logging
db.version(3).stores({
  entries: '++id, date, sync_status',
  users: '++id, username',
  settings: 'key'
});

// Explicitly open the database and handle errors
db.open().then(() => {
  console.log('db: Database opened successfully');
}).catch(err => {
  console.error(`db: CRITICAL - Failed to open database: ${err.name} - ${err.message}`, err);
  if (err.name === 'UpgradeError') {
    console.error('db: Upgrade error detected. You might need to clear browser data for this site.');
  }
});

const handleDbError = (context, error) => {
  const errorInfo = `${error.name || 'UnknownError'}: ${error.message || 'No message'}`;
  console.error(`db: ${context} - ERROR: ${errorInfo}`, error);
  return error;
};

export const addEntry = async (entry) => {
  if (!entry.date) {
    console.error('db: addEntry - Missing date!', entry);
    throw new Error('Ierakstam nepieciešams datums.');
  }
  try {
    console.log(`db: addEntry - Preparing data for date ${entry.date}...`);
    
    // DEBUG: Inspect the object deeply
    for (const key in entry) {
      const val = entry[key];
      const type = typeof val;
      const isArray = Array.isArray(val);
      console.log(`  field: ${key}, type: ${type}, isArray: ${isArray}`);
      if (isArray) {
        val.forEach((item, i) => {
          console.log(`    [${i}]: type=${typeof item}, value=${item}`);
        });
      }
    }

    const existing = await db.entries.where('date').equals(entry.date).first();
    let result;
    
    const payload = {
      ...entry,
      sync_status: entry.sync_status || 'pending',
      updated_at: new Date().toISOString()
    };

    if (existing) {
      console.log(`db: addEntry - Updating existing entry ID ${existing.id}`);
      result = await db.entries.update(existing.id, payload);
    } else {
      console.log('db: addEntry - Adding new entry');
      result = await db.entries.add(payload);
    }
    return result;
  } catch (error) {
    throw handleDbError('addEntry', error);
  }
};

export const getEntries = async () => {
  try {
    console.log('db: getEntries - Fetching all entries...');
    return await db.entries.orderBy('date').reverse().toArray();
  } catch (error) {
    handleDbError('getEntries', error);
    try {
      console.log('db: getEntries - Falling back to toArray()');
      return await db.entries.toArray();
    } catch (fallbackError) {
      handleDbError('getEntries (fallback)', fallbackError);
      return [];
    }
  }
};

export const deleteEntry = async (id) => {
  try {
    console.log(`db: deleteEntry - Deleting ID ${id}`);
    return await db.entries.delete(id);
  } catch (error) {
    throw handleDbError('deleteEntry', error);
  }
};

export const getEntryByDate = async (date) => {
  try {
    console.log(`db: getEntryByDate - Querying ${date}`);
    return await db.entries.where('date').equals(date).first();
  } catch (error) {
    throw handleDbError('getEntryByDate', error);
  }
};
