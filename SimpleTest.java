package com.example;

import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * 简单的测试类，用于触发CI/CD流程
 */
public class SimpleTest {
    
    // 线程不安全的SimpleDateFormat使用
    private static SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
    
    public static void main(String[] args) {
        System.out.println("Hello, CI/CD Test!");
        
        // 可能抛出异常但没有处理
        String date = sdf.format(new Date());
        System.out.println("Current date: " + date);
    }
    
    // 方法抛出通用Exception
    public void testMethod() throws Exception {
        // 空方法体
    }
}
