import java.io.*;

public class FileUtils {
    public static String readFile(String filePath) {
        StringBuilder content = new StringBuilder();
        
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                content.append(line).append("\n");
            }
        } catch (IOException e) {
            System.out.println("读取文件出错：" + e.getMessage());
        }
        
        return content.toString();
    }
    
    public static void writeFile(String filePath, String content) {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(filePath))) {
            bw.write(content);
        } catch (IOException e) {
            System.out.println("写入文件出错：" + e.getMessage());
        }
    }
}