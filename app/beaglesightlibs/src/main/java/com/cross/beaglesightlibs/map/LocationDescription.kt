package com.cross.beaglesightlibs.map

import android.location.Location
import android.location.LocationManager
import android.os.Build
import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.ForeignKey.Companion.CASCADE
import androidx.room.Index
import androidx.room.PrimaryKey
import com.google.android.gms.maps.model.LatLng
import java.util.Locale
import java.util.Objects
import java.util.UUID

@Entity(
    foreignKeys = [ForeignKey(
        entity = Target::class,
        parentColumns = ["id"],
        childColumns = ["targetId"],
        onDelete = CASCADE
    )],
    indices = [Index("targetId")]
)
data class LocationDescription(
    @PrimaryKey val locationId: String = UUID.randomUUID().toString(),
    var targetId: String = UUID.randomUUID().toString(),
    var latlng: LatLng = LatLng(0.0, 0.0),
    var latlng_accuracy: Float = 0f,
    var altitude: Double = 0.0,
    var altitude_accuracy: Float = 0f,
    var lockStatus: LockStatus.Status = LockStatus.Status.WEAK,
    @ColumnInfo(name = "location_description") var description: String? = null
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is LocationDescription) return false
        val that = other
        return java.lang.Double.compare(
            that.latlng.latitude,
            latlng.latitude
        ) == 0 && java.lang.Double.compare(
            that.latlng.longitude,
            latlng.longitude
        ) == 0 && java.lang.Float.compare(
            that.latlng_accuracy,
            latlng_accuracy
        ) == 0 && java.lang.Double.compare(that.altitude, altitude) == 0 && java.lang.Float.compare(
            that.altitude_accuracy,
            altitude_accuracy
        ) == 0 && locationId == that.locationId && targetId == that.targetId && description == that.description && lockStatus == that.lockStatus
    }

    override fun hashCode(): Int {
        return Objects.hash(
            locationId,
            targetId,
            latlng,
            latlng_accuracy,
            altitude,
            altitude_accuracy,
            description,
            lockStatus
        )
    }

    /**
     * Get the distance to a location
     *
     * @param location The location to calculate the distance to
     * @return Distance in meters
     */
    fun distanceTo(location: LocationDescription): Double {
        val pos: LatLng = location.latlng
        val results = FloatArray(2)
        Location.distanceBetween(
            latlng.latitude,
            latlng.longitude,
            pos.latitude,
            pos.longitude,
            results
        )
        return results[0].toDouble()
    }

    /**
     * Get angle to the target
     *
     * @param pos position to the target
     * @return Angle in degrees to the target. Positive means aiming uphill.
     */
    fun pitchTo(pos: LocationDescription): Double {
        val distance = distanceTo(pos)
        val elevation = altitude - pos.altitude
        val radians = Math.atan(elevation / distance)
        return radians * 180 / Math.PI
    }

    val locationString: String
        get() = String.format(
            Locale.ENGLISH,
            "Lat: %.03f Long: %.03f Alt: %.02f",
            latlng.latitude, latlng.longitude, altitude
        )
    val location: Location
        get() {
            val location: Location = Location(LocationManager.GPS_PROVIDER)
            location.latitude = latlng.latitude
            location.longitude = latlng.longitude
            location.altitude = altitude
            location.accuracy = latlng_accuracy
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                location.verticalAccuracyMeters = altitude_accuracy
            }
            return location
        }

}