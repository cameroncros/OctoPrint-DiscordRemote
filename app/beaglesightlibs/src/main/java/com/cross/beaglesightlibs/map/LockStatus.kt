package com.cross.beaglesightlibs.map

import android.location.Location

class LockStatus {
    private var lastLocation: Location? = null
    var status = Status.WEAK
        private set

    enum class Status {
        WEAK, MEDIUM, STRONG
    }

    fun updateLocation(location: Location): Status {
        status = Status.WEAK
        if (lastLocation == null) {
            lastLocation = location
            return status
        }
        val driftx = Math.abs(lastLocation!!.latitude - location.latitude)
        val drifty = Math.abs(lastLocation!!.longitude - location.longitude)
        val driftTotal = Math.sqrt(driftx * driftx + drifty * drifty)
        lastLocation = location
        if (driftTotal < 0.000001 && location.accuracy < 5) {
            status = Status.STRONG
        }
        if (driftTotal < 0.000001 || location.accuracy < 5) {
            status = Status.MEDIUM
        }
        return status
    }
}