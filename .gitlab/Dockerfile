FROM ubuntu:22.04

# install required packages
RUN apt-get update --yes && \
    apt-get install wget gnupg gnupg2 unzip openjdk-17-jdk libx11-dev  \
    libpulse0 libgl1 libnss3 libxcomposite-dev libxcursor1 libasound2 --yes

# export gradle home path
RUN export GRADLE_USER_HOME=$PWD/.gradle

# export android sdk path
ENV ANDROID_SDK_ROOT=$PWD/android-sdk-linux/SDK

# download and unzip commandline tools
# from https://developer.android.com/studio/#command-tools
ARG SDK_TOOLS="9477386"
RUN mkdir -p $ANDROID_SDK_ROOT/cmdline-tools/latest && \
    cd $ANDROID_SDK_ROOT/cmdline-tools/latest && \
    wget --quiet --output-document=commandlinetools.zip https://dl.google.com/android/repository/commandlinetools-linux-${SDK_TOOLS}_latest.zip && \
    echo A | unzip -q commandlinetools.zip && \
    mv cmdline-tools/* ./ && \
    rm commandlinetools.zip

# export android sdk executables paths
ENV PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/:$ANDROID_SDK_ROOT/platform-tools/:$ANDROID_SDK_ROOT/emulator/

# update and install common android sdk components

ARG ANDROID_IMAGE
ARG ANDROID_COMPILE_SDK="33"
ARG ANDROID_BUILD_TOOLS="33.0.2"
RUN $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} --update
RUN echo Y | $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} "platforms;android-${ANDROID_COMPILE_SDK}" "build-tools;${ANDROID_BUILD_TOOLS}"
RUN echo Y | $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} "platform-tools" "emulator" "${ANDROID_IMAGE}"

# download script for emulator waiting
RUN cd $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/ && \
    wget --quiet --output-document=android-wait-for-emulator https://raw.githubusercontent.com/travis-ci/travis-cookbooks/0f497eb71291b52a703143c5cd63a217c8766dc9/community-cookbooks/android-sdk/files/default/android-wait-for-emulator && \
    chmod +x android-wait-for-emulator
