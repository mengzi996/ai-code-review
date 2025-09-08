public class StringUtils {
    
    /**
     * Check if the given string is null or its length is zero (after trimmed)
     */
    public static boolean isBlank(String str) {
        return str == null || str.trim().length() == 0;
    }
  
    /**
     * Trim leading and trailing spaces of the given string
     */
    public static String trim(String str) {
        return str == null ? null : str.trim();
    }
  
    /**
     * Join an array of strings with a delimiter
     */
    public static String join(String[] array, String delimiter) {
        if (array == null || array.length == 0) 
            return "";
            
        StringBuilder sb = new StringBuilder();
        sb.append(array[0]);
        
        for (int i = 1; i < array.length; i++) {
            sb.append(delimiter).append(array[i]);
        }
        
        return sb.toString();
    }
}