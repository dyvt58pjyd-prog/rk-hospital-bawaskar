# Proguard rules for RK Hospital Bawaskar Android Native App
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
