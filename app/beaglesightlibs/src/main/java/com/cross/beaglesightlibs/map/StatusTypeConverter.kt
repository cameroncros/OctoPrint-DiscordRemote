package com.cross.beaglesightlibs.map

import androidx.room.TypeConverter

object StatusTypeConverter {
    @TypeConverter
    fun statusToString(status: LockStatus.Status?): String? {
        return status?.toString()
    }

    @TypeConverter
    fun stringToStatus(string: String?): LockStatus.Status? {
        return if (string == null) {
            null
        } else LockStatus.Status.valueOf(string)
    }
}