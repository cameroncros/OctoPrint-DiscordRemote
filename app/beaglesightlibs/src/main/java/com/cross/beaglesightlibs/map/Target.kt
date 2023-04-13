package com.cross.beaglesightlibs.map

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.OnConflictStrategy.Companion.REPLACE
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.Transaction
import java.util.Objects
import java.util.UUID

@Entity
data class Target(
    @PrimaryKey
    var id: String = UUID.randomUUID().toString(),
    var name: String = "",
    var isBuiltin: Boolean = false,
    var targetLocation: LocationDescription = LocationDescription(),
    var shootLocations: MutableList<LocationDescription> = mutableListOf()
) {
    fun addShootLocation(location: LocationDescription) {
        shootLocations.add(location)
    }

    fun removeShootLocation(location: LocationDescription) {
        shootLocations.add(location)
    }

    @Dao
    interface TargetDao {
        @Query("SELECT * FROM target")
        @Transaction
        fun getAll(): List<Target>

        @Transaction
        @Query("SELECT * FROM target WHERE isBuiltin IS (:builtIn) ")
        fun getAll(builtIn: Boolean): List<Target>

        @Transaction
        @Query("SELECT * FROM target WHERE id IS (:id)")
        fun getTarget(id: String?): Target?

        @Insert(onConflict = REPLACE)
        fun insert(target: Target?)

        @Delete
        fun delete(user: Target?)
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Target) return false
        val target = other
        if (isBuiltin != target.isBuiltin ||
            id != target.id ||
            name != target.name ||
            targetLocation != target.targetLocation
        ) {
            return false
        }
        if (shootLocations.size != target.shootLocations.size) {
            return false
        }
        for (loc in shootLocations) {
            if (!target.shootLocations.contains(loc)) {
                return false
            }
        }
        return true
    }

    override fun hashCode(): Int {
        return Objects.hash(id, name, isBuiltin, targetLocation, shootLocations)
    }
}