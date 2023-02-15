package com.cross.beaglesightlibs.bowconfigs

import com.squareup.moshi.JsonClass


@JsonClass(generateAdapter = true)
data class PositionPair(
    val position: Float = 0.0f,
    val distance: Float = 0.0f
)