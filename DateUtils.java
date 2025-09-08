import java.text.SimpleDateFormat;
import java.util.Date;

public class DateUtils {
    private static ThreadLocal<SimpleDateFormat> sdfThreadLocal = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            return new SimpleDateFormat();
        }
    };

    public static String formatDate(Date date, String pattern) throws Exception {
        SimpleDateFormat sdf = sdfThreadLocal.get();
        synchronized (sdf) {
            sdf.applyPattern(pattern);
            return sdf.format(date);
        }
    }

    public static Date parseDate(String str, String pattern) throws Exception {
        SimpleDateFormat sdf = sdfThreadLocal.get();
        synchronized (sdf) {
            sdf.applyPattern(pattern);
            return sdf.parse(str);
        }
    }
}