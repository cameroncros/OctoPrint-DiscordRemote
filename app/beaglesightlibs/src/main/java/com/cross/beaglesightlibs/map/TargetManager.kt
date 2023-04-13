package com.cross.beaglesightlibs.map

import android.annotation.SuppressLint
import android.content.Context
import android.util.Log
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters

@Database(entities = [Target::class, LocationDescription::class], version = 2)
@TypeConverters(*[StatusTypeConverter::class])
abstract class TargetManager : RoomDatabase() {
    abstract fun targetDao(): Target.TargetDao
    val targets: List<Target>
        get() = targetDao().getAll()

    fun getTargetsWithShootPositions(skipBuiltin: Boolean): List<Target> {
        val targets: List<Target> = targetDao!!.getAll(!skipBuiltin)
        return targets
    }

    fun saveTargets(targets: List<Target>) {
        for (target in targets) {
            saveTarget(target)
        }
    }

    fun deleteTarget(selectedTarget: Target?) {
        // Should CASCADE through and remove all shoot positions as well.
        targetDao!!.delete(selectedTarget)
    }

    fun saveTarget(target: Target) {
        targetDao!!.insert(target)
        val locations = target.shootLocations
        for (location in locations) {
            if (location.targetId != target.id) {
                Log.e("BeagleSight", "Shootlocation has incorrect targetID")
                location.targetId = target.id
            }
        }
    }

    fun getTarget(id: String?): Target? {
        val target: Target = targetDao!!.getTarget(id)
            ?: return null
        return target
    }

    companion object {
        @SuppressLint("StaticFieldLeak")
        @Volatile
        private var instance: TargetManager? = null
        private var targetDao: Target.TargetDao? = null
        fun getInstance(cont: Context?): TargetManager? {
            synchronized(TargetManager::class.java) {
                if (instance == null && cont != null) {
                    instance = Room.databaseBuilder(cont, TargetManager::class.java, "targets")
                        .build()
                    targetDao = instance!!.targetDao()
                }
            }
            return instance
        }
    }
}